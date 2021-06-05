import serial
import struct

# https://github.com/pimoroni/pms5003-python/blob/master/library/pms5003/__init__.py
class PMS5003Data():
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data = struct.unpack(">BB" + 13 * 'H' + "BBH", raw_data)

        if self.data[0] != ord('B') or self.data[1] != ord('M'):
             raise Exception(f"Header not found. Received {chr(self.data[0])}{chr(self.data[1])}, expected BM")
        if self.data[2] != 28:
             raise Exception(f"Unexpected message length. Received {str(self.data[2])}, expected 28")

        self.data = self.data[3:]
        self.checksum = self.data[13]

    def pm_ug_per_m3(self, size, atmospheric_environment=False):
        if atmospheric_environment:
            if size == 1.0:
                return self.data[3]
            if size == 2.5:
                return self.data[4]
            if size is None:
                return self.data[5]

        else:
            if size == 1.0:
                return self.data[0]
            if size == 2.5:
                return self.data[1]
            if size == 10:
                return self.data[2]

        raise ValueError(f"Particle size {size} measurement not available.")

    def pm_per_1l_air(self, size):
        if size == 0.3:
            return self.data[6]
        if size == 0.5:
            return self.data[7]
        if size == 1.0:
            return self.data[8]
        if size == 2.5:
            return self.data[9]
        if size == 5:
            return self.data[10]
        if size == 10:
            return self.data[11]

        raise ValueError(f"Particle size {size} measurement not available.")

    def debug(self):
        return f"S0 Data: {repr(self.raw_data)}"

    def __repr__(self):
        return """
PM1.0 ug/m3 (ultrafine particles):                             {}
PM2.5 ug/m3 (combustion particles, organic compounds, metals): {}
PM10 ug/m3  (dust, pollen, mould spores):                      {}
PM1.0 ug/m3 (atmos env):                                       {}
PM2.5 ug/m3 (atmos env):                                       {}
PM10 ug/m3 (atmos env):                                        {}
>0.3um in 0.1L air:                                            {}
>0.5um in 0.1L air:                                            {}
>1.0um in 0.1L air:                                            {}
>2.5um in 0.1L air:                                            {}
>5.0um in 0.1L air:                                            {}
>10um in 0.1L air:                                             {}
""".format(*self.data[:-2], checksum=self.checksum)

    def __str__(self):
        return self.__repr__()

while True:
    port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=5.0)
    parsed = PMS5003Data(port.read(32))
    print(parsed)

