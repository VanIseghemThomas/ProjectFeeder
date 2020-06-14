import smbus
import time

class LCD:
    LCD_WIDTH = 16      # Maximum characters per line

    LCD_CHR = 1     # Mode - Sending data
    LCD_CMD = 0     # Mode - Sending command

    LCD_LINE_1 = 0x80   # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0   # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94   # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4   # LCD RAM address for the 4th line

    LCD_BACKLIGHT = 0x08  # On

    ENABLE = 0b00000100     # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    # Open I2C interface
    bus = smbus.SMBus(1)    # Rev 2 Pi uses 1

    def __init__(self, address=0x27):
        self._addr = address 
        self._lcd_init()

    def _lcd_init(self):
        # Initialise display
        self._lcd_byte(0x33, LCD.LCD_CMD)     # 110011 Initialise
        self._lcd_byte(0x32, LCD.LCD_CMD)     # 110010 Initialise
        self._lcd_byte(0x06, LCD.LCD_CMD)     # 000110 Cursor move direction
        self._lcd_byte(0x0C, LCD.LCD_CMD)     # 001100 Display On,Cursor Off, Blink Off
        self._lcd_byte(0x28, LCD.LCD_CMD)     # 101000 Data length, number of lines, font size
        self._lcd_byte(0x01, LCD.LCD_CMD)     # 000001 Clear display
        time.sleep(LCD.E_DELAY)


    def _lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        bits_high = mode | (bits & 0xF0) | LCD.LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD.LCD_BACKLIGHT

        # High bits
        LCD.bus.write_byte(self._addr, bits_high)
        self._lcd_toggle_enable(bits_high)

        # Low bits
        LCD.bus.write_byte(self._addr, bits_low)
        self._lcd_toggle_enable(bits_low)


    def _lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(LCD.E_DELAY)
        LCD.bus.write_byte(self._addr, (bits | LCD.ENABLE))
        time.sleep(LCD.E_PULSE)
        LCD.bus.write_byte(self._addr, (bits & ~LCD.ENABLE))
        time.sleep(LCD.E_DELAY)


    def write_string(self, message, line):
        # Send string to display
        message = message.ljust(LCD.LCD_WIDTH, " ")

        if line == 0:
            line = LCD.LCD_LINE_1

        elif line == 1:
            line = LCD.LCD_LINE_2

        self._lcd_byte(line, LCD.LCD_CMD)

        for i in range(LCD.LCD_WIDTH):
            self._lcd_byte(ord(message[i]), LCD.LCD_CHR)
