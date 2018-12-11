from device import Device
import time

# ------------------------------
# Create devices
# ------------------------------
device_list = []
device_list.append(Device( 'octa-robin', '493332340046001e', 0, [1,1] ))   # TTN Device ID, DASH7 Hardware ID, bool training_mode, location=[x,y]
device_list.append(Device( 'octa-thomas', '4933323400280025', 0, [999,999] ))

# ------------------------------
# Loop
# ------------------------------
while True:
    time.sleep(60)
