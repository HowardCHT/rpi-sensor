import busio
import adafruit_ccs811
from board import *
import time

i2c_bus = busio.I2C(SCL, SDA)

ccs = adafruit_ccs811.CCS811(i2c_bus)

if __name__ == "__main__":

    while True:
        try:
            print("CO2: ", ccs.eco2, " TVOC:", ccs.tvoc)
        except Exception as identifier:
            break
        else:
            time.sleep(.5)
