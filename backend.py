from device import Device
import time
import threading

# ------------------------------
# Create devices
# ------------------------------
device_list = []
device_list.append(threading.Thread(target=Device, args=[ 'octa-robin',  '493332340046001e', 0, [2,2] ]).start()) # args=[ device_name, device_id, training_mode, training_location[x,y] ]
device_list.append(threading.Thread(target=Device, args=[ 'octa-thomas', '4933323400280025', 0, [999,999] ]).start())
device_list.append(threading.Thread(target=Device, args=[ 'octa-toon', '0010962A80AEB62D', 0, [999,999] ]).start())

# ------------------------------
# Loop
# ------------------------------
while True:
    time.sleep(60)
