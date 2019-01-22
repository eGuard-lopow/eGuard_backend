# -*- coding: utf-8 -*-
from __future__ import print_function
import paho.mqtt.client as mqtt # import the client
from thingsboard import Thingsboard
import time
import threading
import json
import base64
import os
import logging
import datetime
from parser import parse_alp
from localization import Localization

logger = logging.getLogger(__name__)

class Device:

    # ------------------------------
    # Broker addresses
    # ------------------------------
    broker_address_lora='eu.thethings.network'
    broker_address_d7='backend.idlab.uantwerpen.be'

    # ------------------------------
    # Load keys
    # ------------------------------
    with open('keys.json') as f:
        keys = json.load(f)

    thingsboard = Thingsboard(keys['thingsboard']['url'], 1883, keys['thingsboard']['access_token'])

    def __init__(self, device_name, device_id, training_mode, location ):
        self.device_name = device_name
        self.device_id = device_id
        self.training_mode = training_mode
        self.x_training_location = location[0]
        self.y_training_location = location[1]
        self.localization = Localization( 'mongodb://localhost:27017/', 'd7mockup', 'dipole' )     # ( host, db, collection )
        self.queue_d7 = {}                      # empty queue for dash-7 deduplication and rssi values
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
        print('time: '+str(datetime.datetime.now()))
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
        time.sleep(1)
        print('-------------------- Dash-7 Process --------------------')
        print('queue',self.queue_d7)
        if self.training_mode:
            # -------------------------
            # Add Fingerprint to Database
            # -------------------------
            # x_training_location = input('X position >')
            # y_training_location = input('Y position >')
            self.localization.train( self.x_training_location, self.y_training_location, self.queue_d7 ) # add to training database ( x_value, y_value, rx_values )
            print('Entry added to database')

        # -------------------------
        # Localize
        # -------------------------
        location = self.localization.localize( self.queue_d7, 25 )  # get location based on fingerprinting (rx_values, k-nearest neighbors)
        print('Location is approximately x:'+str(location['x'])+' y:'+str(location['y']))

        # print('')
        # for y in range(0,3):
        #     print(str(y), end='')
        #     if round(location['y']) == y:
        #         print(' '+' '*2*int(round(location['x']))+'X')
        #     else:
        #         print(' ')
        # print('  0 1 2 3 4 5 6')
        # print('')

        print('')
        for y in range(0,3):
            print(str(y), end='')
            for x in range(0,6):
                if y == round(location['y']) and x == round(location['x']):
                    print(str(' X'), end='')
                else:
                    print(str(' •'), end='')
            print('')
        print('  0 1 2 3 4 5')
        print('')

        # -------------------------
        # Done
        # -------------------------
        self.queue_d7 = {}                   # clear queue
        if not self.training_mode:
            self.process_data(data, device_id, location)   # process data of first received packet
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
        self.process_data(data, payload['hardware_serial'], None)
        print('---------------------------------------------')

    def process_data(self, data, device_id, location):
        print('data: '+str(data))
        # -------------------------
        # Alerts
        # -------------------------
        alerts = data[0]
        alert_fall        = (alerts & 0b00000010) > 0
        alert_temperature = (alerts & 0b00000100) > 0
        alert_humidity    = (alerts & 0b00001000) > 0
        print('Fall alert detected: '+str(alert_fall))
        print('Temperature alert detected: '+str(alert_temperature))
        print('Humidity alert detected: '+str(alert_humidity))
        # -------------------------
        # Temperature & Humidity
        # -------------------------
        temperature = float((data[2]<<8)|data[1])/100
        humidity = float((data[4]<<8)|data[3])/100
        print('Temperature [C]: '+str(temperature))
        print('Relative Humidity [%]: '+str(humidity))
        # -------------------------
        # Light Sensor
        # -------------------------
        light = data[5]
        dark     =                 light <=  20
        indoor   =  20 < light and light <= 230
        sunlight = 230 < light
        print('detected light level is '+str(light),end='')
        if dark:
            print(' which corresponds to dark')
        elif indoor:
            print(' which corresponds to indoor')
        elif sunlight:
            print(' which corresponds to direct sunlight')
        # -------------------------
        # GPS
        # -------------------------
        latitude = float((data[6]<<24)|(data[7]<<16)|(data[8]<<8)|data[9])/1000000
        longitude = float((data[10]<<24)|(data[11]<<16)|(data[12]<<8)|data[13])/1000000
        print('Latitude: '+str(latitude))
        print('Longitude: '+str(longitude))
        # -------------------------
        # Send to Thingsboard
        # -------------------------
        print('Sending data to ThingsBoard')
        current_ts_ms = int(round(time.time() * 1000))   # current timestamp in milliseconds, needed for Thingsboard
        # send non-numeric data ('attributes') to Thingsboard as JSON. Example:
        # thingsboard_attributes = {'last_data_rate': str(payload['metadata']['data_rate'])}
        # thingsboard.sendDeviceAttributes(device_id, thingsboard_attributes)
        # send numeric data ('telemetry') to Thingsboard as JSON (only floats or integers!!!). Example:
        thingsboard_telemetry = {'alert_fall':  alert_fall, 'alert_temperature':  alert_temperature, 'alert_humidity':  alert_humidity, 'temperature': temperature, 'humidity': humidity, 'light_level': light, 'latitude': latitude, 'longitude': longitude}
        if location != None:
            thingsboard_telemetry['x'] = float(location['x'])
            thingsboard_telemetry['y'] = float(location['y'])

        # if location == None:
        #     thingsboard_telemetry = {'alert_fall':  alert_fall, 'alert_temperature':  alert_temperature, 'alert_humidity':  alert_humidity, 'temperature': temperature, 'humidity': humidity, 'light_level': light, 'latitude': latitude, 'longitude': longitude}
        # else:
        #     thingsboard_telemetry = {'alert_fall':  alert_fall, 'alert_temperature':  alert_temperature, 'alert_humidity':  alert_humidity, 'temperature': temperature, 'humidity': humidity, 'light_level': light, 'latitude': latitude, 'longitude': longitude, 'x': float(location['x']), 'y': float(location['y'])}
        self.thingsboard.sendDeviceTelemetry(device_id.lower(), current_ts_ms, thingsboard_telemetry)
