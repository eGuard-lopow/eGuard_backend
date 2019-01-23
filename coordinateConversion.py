import math

def degreesToCoordinates(latitude_deg, longitude_deg):
    print("Complete lat:", latitude_deg)
    print("Complete lat:", longitude_deg)
    # latitude_deg = math.floor(latitude_deg * 10000000)
    # longitude_deg = math.floor(longitude_deg * 10000000)

    latitude_sec = latitude_deg % 100000
    longitude_sec = longitude_deg % 100000
    latitude_sec = latitude_sec/1000
    longitude_sec = longitude_sec/1000

    latitude_deg = math.floor(latitude_deg / 100000)
    longitude_deg = math.floor(longitude_deg / 100000)
    latitude_min = latitude_deg % 100
    longitude_min = longitude_deg % 100

    latitude_deg = math.floor(latitude_deg / 100)
    longitude_deg = math.floor(longitude_deg / 100)
    latitude_deg = latitude_deg % 100
    longitude_deg = longitude_deg % 100

    print("Graden lat:", latitude_deg)
    print("Graden lon:", longitude_deg)

    print("Minuten lat:", latitude_min)
    print("Minuten lon:", longitude_min)

    print("Seconden lat:", latitude_sec)
    print("Seconden lon:", longitude_sec)

    latitude_dec = latitude_deg + latitude_min/60 + latitude_sec/60/100
    print("Latitude decimal:", latitude_dec)

    longitude_dec = longitude_deg + longitude_min/60 + longitude_sec/60/100
    print("Latitude decimal:", longitude_dec)
    print("coordinates decimal: (", latitude_dec, ",", longitude_dec, ")")

    return latitude_dec, longitude_dec
