from device import Device
import time
import threading

# ------------------------------
# Create devices
# ------------------------------
# device_list = []
device_list.append(threading.Thread(target=Device, args=[ 'octa-robin', '493332340046001e', 1, [0,0] ]).start())
device_list.append(threading.Thread(target=Device, args=[ 'octa-thomas', '4933323400280025', 0, [999,999] ]).start())
device_list.append(threading.Thread(target=Device, args=[ 'foo-joris',  '4933323400370020', 1, [0,1] ]).start())
device_list.append(threading.Thread(target=Device, args=[ 'foo-wesley', '49333234002e0020', 1, [0,2] ]).start())

# ------------------------------
# Loop
# ------------------------------
while True:
    time.sleep(60)
