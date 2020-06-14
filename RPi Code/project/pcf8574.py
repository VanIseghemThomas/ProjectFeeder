from RPi import GPIO
import time

class Pcf8574:
    debug = False
    GPIO.setwarnings(False)
    def __init__(self, SDA, SCL, address):
        GPIO.setmode(GPIO.BCM)
        self._SDA = SDA
        self._SCL = SCL
        GPIO.setup(SDA, GPIO.OUT)
        GPIO.setup(SCL, GPIO.OUT)
        self._address = address
        self.dot = False
        self._delay = 0.0001

    def __start_conditie(self):
        # 1 1
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 1)
        time.sleep(self._delay)
        # 0 1
        GPIO.output(self.SDA, 0)
        time.sleep(self._delay)
        # 0 0
        GPIO.output(self.SCL, 0)
        time.sleep(self._delay)

    def __stop_conditie(self):
        # 0 0
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 0)
        time.sleep(self._delay)
        # 1 0
        GPIO.output(self.SCL, 1)
        time.sleep(self._delay)
        # 1 1
        GPIO.output(self.SDA, 1)
        time.sleep(self._delay)

    def __writebit(self, bit):
        # Data
        GPIO.output(self.SDA, bit)
        # Klok aan-uit
        GPIO.output(self.SCL, 1)
        time.sleep(self._delay)
        GPIO.output(self.SCL, 0)
        time.sleep(self._delay)

    def __writebyte(self, byte):
        # Puntje eventueel toevoegen
        if (self._dot):
            byte = byte & 0b01111111
        # Byte bit per bit uitschrijven
        mask = 0b10000000
        for i in range(0,8):
            self.__writebit(byte & mask)
            mask = mask >> 1

    def __ack(self):
        # 1. Setup input pullup van de SDA pin
        GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # 2. klok omhoog brengen
        GPIO.output(self.SCL, 1)

        # 3. SDA pin inlezen
        waarde = GPIO.input(self.SDA)
        if (Pcf8574.debug):
            if (not waarde):
                # Laag = OK
                print("Acknowledge")
            else:
                # NOK
                print("Got no acknowledge")

        # 4. Setup output van de SDA pin
        GPIO.setup(self.SDA, GPIO.OUT)
        # 5. klok terug omlaag.
        GPIO.output(self.SCL, 0)

        return not waarde

    def write_outputs(self, data):
        # start
        self.__start_conditie()
        # adres
        self.__writebyte(self.address << 1)
        # ack
        acknowledge = self.__ack()
        # data
        self.__writebyte(data)
        # ack
        self.__ack()
        # stop
        self.__stop_conditie

        return acknowledge

    @property
    def dot(self):
        """The dot property."""
        return self._dot
    @dot.setter
    def dot(self, value):
        self._dot = value

    @property
    def address(self):
        """The address property."""
        return self._address

    @property
    def SDA(self):
        """The SDA property."""
        return self._SDA

    @property
    def SCL(self):
        """The SCL property."""
        return self._SCL