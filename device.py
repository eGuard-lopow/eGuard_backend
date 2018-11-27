import paho.mqtt.client as mqtt # import the client
from thingsboard import Thingsboard
import time
import threading
import json
import base64
import os
import logging
from parser import parse_alp
import pymongo
import numpy as np

logger = logging.getLogger(__name__)

class Device:

    # ------------------------------
    # Broker addresses
    # ------------------------------
    broker_address_lora='eu.thethings.network'
    broker_address_d7='backend.idlab.uantwerpen.be'

    gateway_ids=['4337313400210032', '433731340023003d', '42373436001c0037', '463230390032003e']

    # ------------------------------
    # Load keys
    # ------------------------------
    with open('keys.json') as f:
        keys = json.load(f)

    thingsboard = Thingsboard(keys['thingsboard']['url'], 1883, keys['thingsboard']['access_token'])

    def __init__(self, device_name, device_id):
        self.device_name = device_name
        self.device_id = device_id
        self.queue_d7 = {}                      # empty queue for dash-7 deduplication and rssi values
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
        # db_list = self.mongo_client.list_database_names()
        # print(db_list)
        # if 'd7mockup' in db_list:
        #     print('The database exists.')
        self.db = self.mongo_client['d7mockup']
        # print(self.db.list_collection_names())
        self.collection = self.db['fingerprints2']
        self.training_counter = 0
        self.processor = threading.Thread()     # empty thread object
        # ------------------------------
        # Subscribe to Dash-7
        # ------------------------------
        try:
            self.client_d7 = mqtt.Client() #create new instance
            self.client_d7.on_message=self.on_message_d7 #attach function to callback
            # self.client_d7.on_connect=self.on_connect
            print('connecting to broker '+self.broker_address_d7)
            self.client_d7.connect(self.broker_address_d7) #connect to broker
            self.client_d7.loop_start()
            print('Subscribing to topic '+'/d7/'+self.device_id+'/#')
            # self.client_d7.subscribe('/d7/#')
            self.client_d7.subscribe('/d7/'+self.device_id+'/#')
        except:
            print('connecting to Dash-7 backend failed')
        # ------------------------------
        # Subscribe to LoRaWAN
        # ------------------------------
        try:
            self.client_lora = mqtt.Client() #create new instance
            self.client_lora.username_pw_set(self.keys['ttn']['app_id'], self.keys['ttn']['access_key'])
            self.client_lora.on_message=self.on_message_lora #attach function to callback
            print('connecting to broker '+self.broker_address_lora)
            self.client_lora.connect(self.broker_address_lora) #connect to broker
            self.client_lora.loop_start()
            print('Subscribing to topic '+'eguard/devices/'+device_name+'/up')
            self.client_lora.subscribe('eguard/devices/'+device_name+'/up')
        except:
            print('connecting to The Things Network failed')

    def __del__(self):
        self.client_d7.loop_stop()
        self.client_lora.loop_stop()

    def on_message_d7(self, client, userdata, message):
        print('--------------- Dash-7 Received ---------------')
        raw = str(message.payload.decode('utf-8'))
        print('message topic: '+str(message.topic))
        hardware_id = message.topic.split('/')[2]
        gateway_id = message.topic.split('/')[3]
        print('hardware_id: '+hardware_id)
        print('message qos: '+str(message.qos))
        print('message retain flag: '+str(message.retain))
        print('raw message: '+raw)
        dict = parse_alp(raw)
        print(dict)
        self.queue_d7[gateway_id] = int(dict['rx_level'])   # save rx_level for every receiving gateway
        # obj = {}
        # obj['gatewayID'] = str(gateway_id)
        # obj['rx_level'] = str(dict['rx_level'])
        # self.queue_d7.append(obj)
        print('queue',self.queue_d7)
        print('thread',self.processor.is_alive())
        if not self.processor.is_alive():
            print('Thread started')
            self.processor = threading.Thread(target=self.process_data_counter, args=[dict['data'], hardware_id])
            print('Thread created')
            self.processor.start()
            print('Thread started')
        print('-----------------------------------------------')

    def process_data_counter(self, data, device_id):
        time.sleep(5)
        print('-------------------- Dash-7 Process --------------------')
        print('queue',self.queue_d7)
        if False:
            # -------------------------
            # Add to Training Database
            # -------------------------
            # x_in = input('X position >')
            # y_in = input('Y position >')
            x_in = 6
            y_in = 1
            mydict = { 'x': x_in,'y': y_in, 'gateways': self.queue_d7}
            self.collection.insert_one(mydict)
            print('Entry added to MongoDB')
            self.training_counter += 1
            print('Trainingcounter = '+str(self.training_counter))
        if True: # else:
            # -------------------------
            # Localize
            # -------------------------
            probablistic = []
            print('Docs:')
            for document in self.collection.find():
                print(document) # iterate the cursor
                diff = []
                for gateway_id in self.gateway_ids:
                    if gateway_id not in self.queue_d7:
                        self.queue_d7[gateway_id] = 200 # out of range
                    if gateway_id not in document['gateways']:
                        document['gateways'][gateway_id] = 200 # out of range
                    diff.append( int(self.queue_d7[gateway_id])-int(document['gateways'][gateway_id]) )
                print(diff)
                rms = np.sqrt(np.mean(np.square(diff)))
                print(rms)
                probablistic.append({'x': document['x'],'y': document['y'],'rms':rms})
            print(probablistic)
            # lowest_rms = 999999  # unrealistic high
            # x = 0
            # y = 0
            # for point in probablistic:
            #     if point['rms']<lowest_rms:
            #         lowest_rms = point['rms']
            #         x = point['x']
            #         y = point['y']

            ordered_locations = sorted(probablistic, key = lambda i: i['rms']) # sort on RMS value
            k = 5 # amount of neighbors
            nearest_neighbors = ordered_locations[:k]
            print('knn: '+str(nearest_neighbors))
            # -------------------------
            # Mean Value
            # -------------------------

            # for location in nearest_neighbors:
            #     x += location['x']
            #     y += location['y']
            # x=x/len(x)
            # y=x/len(x)

            # -------------------------
            # Weighted Average
            # -------------------------
            x = 0
            y = 0
            total_weight = 0
            for location in nearest_neighbors:
                if location['rms']==0:
                    weight = 100
                else:
                    weight = 1/location['rms']
                x += int(location['x']) * weight
                y += int(location['y']) * weight
                total_weight += weight
            x=x/total_weight
            y=y/total_weight
            print('Location is approximately x:'+str(x)+' y:'+str(y))

        # -------------------------
        # Done
        # -------------------------
        self.queue_d7 = {}                   # clear queue
        self.process_data(data, device_id)   # process data of first received packet
        print('--------------------------------------------------------')

    def on_message_lora(self, client, userdata, message):
        print('--------------- LoRa Received ---------------')
        payload = str(message.payload.decode('utf-8'))
        print('message received: '+payload)
        print('message topic: '+str(message.topic))
        print('message qos: '+str(message.qos))
        print('message retain flag: '+str(message.retain))
        payload = json.loads(payload)
        print('payload: '+str(payload))
        payload_raw = str(payload['payload_raw'])
        print('payload_raw: '+payload_raw)

        bin = base64.b64decode(str(payload_raw))
        print('bin: '+bin)
        hex = bin.encode('hex')
        print('hex: ',hex)

        data = []
        for i in range(8, len(hex), 2):   # ignore first 4 bytes (= 8 niples)
            data.append(int(hex[i:i+2],16)) # convert hex byte to int
        self.process_data(data, payload['hardware_serial'])
        print('---------------------------------------------')

    def process_data(self, data, device_id):
        print('data: '+str(data))
        temperature = float((data[1]<<8)|data[0])/100
        humidity = float((data[3]<<8)|data[2])/100
        print('Temperature [C]: '+str(temperature))
        print('Relative Humidity [%]: '+str(humidity))
        # -------------------------
        # Send to Thingsboard
        # -------------------------
        print('Sending data to ThingsBoard')
        current_ts_ms = int(round(time.time() * 1000))   # current timestamp in milliseconds, needed for Thingsboard
        # send non-numeric data ('attributes') to Thingsboard as JSON. Example:
        # thingsboard_attributes = {'last_data_rate': str(payload['metadata']['data_rate'])}
        # thingsboard.sendDeviceAttributes(device_id, thingsboard_attributes)
        # send numeric data ('telemetry') to Thingsboard as JSON (only floats or integers!!!). Example:
        thingsboard_telemetry = {'temperature': temperature,
                                 'humidity': humidity}
                                 # 'latitude': float(payload['latitude']),
                                 # 'longitude': float(payload['longitude'])}
        self.thingsboard.sendDeviceTelemetry(device_id.lower(), current_ts_ms, thingsboard_telemetry)
