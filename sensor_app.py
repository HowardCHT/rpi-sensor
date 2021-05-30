import busio
import adafruit_ccs811
import board
import time
import threading
import adafruit_bme280
import SDL_Pi_HDC1080
from flask import Flask, jsonify

app = Flask(__name__)


class CJMCU8128:
    def __init__(self):
        # CCS811
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.ccs = adafruit_ccs811.CCS811(self.i2c_bus)
        self.ccs_flg = False

        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c_bus)
        self.bme280.sea_level_pressure = 1013.25
        self.bme280_flg = False

        self.hdc1080 = SDL_Pi_HDC1080.SDL_Pi_HDC1080()
        self.hdc1080_flg = False

        self.__data = {
            # CCS811
            "CO2": None,
            "TVOC": None,
            # bme280
            "Temperature": None,
            "RelativeHumidity": None,
            "Pressure": None,
            "Altitude": None,
            # hdc1080
            "Temperature_HDC1080": None,
            "Humidity_HDC1080": None
        }

    def run_ccs(self):
        print(" ==== run_ccs ====")
        while self.ccs_flg:
            try:
                self.__data["CO2"] = self.ccs.eco2
                self.__data["TVOC"] = self.ccs.tvoc
            except Exception as identifier:
                print(f"Exception => {identifier}")
                break
            else:
                time.sleep(1)

    def run_bme280(self):
        print(" ==== run_bme280 ====")
        while self.bme280_flg:
            try:
                self.__data["Temperature"] = self.bme280.temperature
                self.__data["RelativeHumidity"] = self.bme280.relative_humidity
                self.__data["Pressure"] = self.bme280.pressure
                self.__data["Altitude"] = self.bme280.altitude
            except Exception as identifier:
                print(f"Exception => {identifier}")
                break
            else:
                time.sleep(3)

    def run_hdc1080(self):
        while self.hdc1080_flg:
            try:
                self.__data["Temperature_HDC1080"] = self.hdc1080.readTemperature()
                self.__data["Humidity_HDC1080"] = self.hdc1080.readHumidity()
            except Exception as identifier:
                print(f"Exception => {identifier}")
                break
            else:
                time.sleep(1)

    def start(self):
        self.ccs_flg = True
        t_ccs = threading.Thread(target=self.run_ccs)
        t_ccs.start()

        self.bme280_flg = True
        t_bme280 = threading.Thread(target=self.run_bme280)
        t_bme280.start()

        self.hdc1080_flg = True
        t_hdc1080 = threading.Thread(target=self.run_hdc1080)
        t_hdc1080.start()

    def stop(self):
        self.ccs_flg = False
        self.bme280_flg = False
        self.hdc1080_flg = False

    @property
    def get_data(self):
        return self.__data


c_sensor = CJMCU8128()


@app.route("/getdata", methods=['GET'])
def getdata():
    return jsonify(c_sensor.get_data)


if __name__ == "__main__":
    c_sensor.start()
    app.run(host="0.0.0.0", port=3000, debug=False)
    c_sensor.stop()
