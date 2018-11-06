from device import Device
import time

# ------------------------------
# Create devices
# ------------------------------
device_list = []
device_list.append(Device('octa-robin','493332340046001e'))
device_list.append(Device('octa-thomas','4933323400280025'))

# ------------------------------
# Loop
# ------------------------------
while True:
    time.sleep(60)
