import paho.mqtt.client as mqtt # import the client
from thingsboard import Thingsboard
import time
import json
import base64
import os
from parser import parse_alp

def on_message_d7(client, userdata, message):
    print("--------------- Dash-7 Received ---------------")
    raw = str(message.payload.decode("utf-8"))
    print("message topic: "+str(message.topic))
    hardware_id = message.topic.split('/')[2]
    print("hardware_id: "+hardware_id)
    print("message qos: "+str(message.qos))
    print("message retain flag: "+str(message.retain))
    print("raw message: "+raw)
    data = parse_alp(raw)
    process_data(data, hardware_id)
    print("-----------------------------------------------")

def on_message_lora(client, userdata, message):
    print("--------------- LoRa Received ---------------")
    payload = str(message.payload.decode("utf-8"))
    print("message received: "+payload)
    print("message topic: "+str(message.topic))
    print("message qos: "+str(message.qos))
    print("message retain flag: "+str(message.retain))
    payload = json.loads(payload)
    print("payload: "+str(payload))
    payload_raw = str(payload['payload_raw'])
    print("payload_raw: "+payload_raw)

    bin = base64.b64decode(str(payload_raw))
    print("bin: "+bin)
    hex = bin.encode('hex')
    print("hex: ",hex)

    data = []
    for i in range(8, int(len(hex)), 2):   # ignore first 4 bytes (= 8 niples)
        data.append(int(hex[i:i+2],16)) # convert hex byte to int
    process_data(data, payload["hardware_serial"])
    print("---------------------------------------------")

def process_data(data, device_id):
    print("data: "+str(data))
    if device_id in device_list:
        print('----- Known Device ('+device_id+') -----')
        temperature = float((data[1]<<8)|data[0])/100
        humidity = float((data[3]<<8)|data[2])/100
        print("Temperature [C]: "+str(temperature))
        print("Relative Humidity [%]: "+str(humidity))
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
        thingsboard.sendDeviceTelemetry(device_id.lower(), current_ts_ms, thingsboard_telemetry)


# ------------------------------
# Load keys
# ------------------------------
with open('keys.json') as f:
    keys = json.load(f)

broker_address_lora="eu.thethings.network"
broker_address_d7="backend.idlab.uantwerpen.be"

device_list = ['493332340046001e']

thingsboard = Thingsboard(keys['thingsboard']['url'], 1883, keys['thingsboard']['access_token'])

print("creating new instance")
client_d7 = mqtt.Client() #create new instance
client_d7.on_message=on_message_d7 #attach function to callback
print("connecting to broker")
client_d7.connect(broker_address_d7) #connect to broker

print("creating new instance")
client_lora = mqtt.Client() #create new instance
client_lora.username_pw_set(keys['ttn']['app_id'], keys['ttn']['access_key'])
client_lora.on_message=on_message_lora #attach function to callback
print("connecting to broker")
client_lora.connect(broker_address_lora) #connect to broker

client_d7.loop_start() #start the loop
client_lora.loop_start() #start the loop
print("Subscribing to topic","/d7/#")
client_d7.subscribe("/d7/#")
print("Subscribing to topic","+/devices/+/up")
client_lora.subscribe("+/devices/+/up")

while True:
    time.sleep(60) # wait

client_d7.loop_stop() #stop the loop
client_lora.loop_stop() #stop the loop
