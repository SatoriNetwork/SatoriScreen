################################################################################
#                                                                              #
#  Script: SATORI & EVRMORE Wallet Monitor                                     #
#  Description: Connects to wallet APIs to retrieve EVR balance, specific      #
#               asset balances (e.g., SATORI, LOLLIPOP), and displays the data #
#               on a 2.9" ePaper display. Includes price updates and visuals.  #
#                                                                              #
#                                                                              #
#  Features:                                                                   #
#      - Retrieves EVR balance and selected asset balances.                    #
#      - Fetches live price data for SATORI.                                   #
#      - Displays data on an ePaper display with custom visuals (bitmaps).     #
#      - Updates regularly (once per hour) and fetches accurate NTP time.      #
#      - Includes flexible text scaling and bitmap drawing tools.              #
#                                                                              #
#  Author: https://github.com/JohnConnorNPC  X: @jc0839 Discord: @jc0839       #
#  License: MIT                                                                #
#  Version: 0.1.1                                                             #
#                                                                              #
################################################################################


import network
import urequests
from machine import Pin, SPI
import framebuf
import utime
import socket
import time
import struct
import machine

# Wi-Fi credentials
SSID = "YOUR-WIFI-SSID"
PASSWORD = "YOUR-WIFI-PASSWORD"

TIMEZONE_GMT_OFFSET=10
DATE_FORMAT="AU"
#DATE_FORMAT="US"

SHOW_DAILY_CHANGE=True #NOT IMPLIMENTED YET

WALLET_ADDRESSES = [
    "EXJxFagCoEyfF4E3v5xjXShcpyvdQgFP4C",
    "EXfMF1w2x65eZtK3jKHuAa28EBngqW8RnC",
    "Ec1pNjD7CxDjQGcjyD3TZ4ayZ3thRkJqoM"
]

# Pin definitions
RST_PIN = 12
DC_PIN = 8
CS_PIN = 9
BUSY_PIN = 13

# Display resolution
EPD_WIDTH = 128
EPD_HEIGHT = 296

SATORI_BITMAP = [
    0b00000000, 0b00000000, 0b00000000, 0b00000000,  # Row 1
    0b00000000, 0b00000111, 0b11000000, 0b00000000,  # Row 2
    0b00000000, 0b00111111, 0b11111100, 0b00000000,  # Row 3
    0b00000000, 0b11111111, 0b11111111, 0b00000000,  # Row 4
    0b00000001, 0b11110000, 0b00000111, 0b10000000,  # Row 5
    0b00000011, 0b11000000, 0b00000011, 0b11000000,  # Row 6
    0b00000111, 0b00000000, 0b00000000, 0b11100000,  # Row 7
    0b00001110, 0b00000000, 0b00000000, 0b01110000,  # Row 8
    0b00011100, 0b00000000, 0b00000000, 0b00111000,  # Row 9
    0b00011100, 0b00000000, 0b00000000, 0b00011000,  # Row 10
    0b00111000, 0b00000000, 0b00000000, 0b00011100,  # Row 11
    0b00111000, 0b00000000, 0b00000000, 0b00001101,  # Row 12
    0b00110000, 0b00000000, 0b00000000, 0b00001100,  # Row 13
    0b01110000, 0b00000000, 0b00000000, 0b00000110,  # Row 14
    0b01110000, 0b00000000, 0b00000000, 0b00000110,  # Row 15
    0b01110000, 0b00000000, 0b00000000, 0b00000110,  # Row 16
    0b01110000, 0b00000000, 0b10000000, 0b00000110,  # Row 17
    0b01110000, 0b00000000, 0b10000000, 0b00000110,  # Row 18
    0b00110000, 0b00000001, 0b11000000, 0b00000110,  # Row 19
    0b00111000, 0b00000001, 0b11000000, 0b00001100,  # Row 20
    0b00111000, 0b00000001, 0b10000000, 0b00001101,  # Row 21
    0b00011100, 0b00000011, 0b11100000, 0b00001000,  # Row 22
    0b00011100, 0b00000111, 0b11110000, 0b00001000,  # Row 23
    0b00001110, 0b00000111, 0b11110000, 0b00010000,  # Row 24
    0b00100111, 0b00000101, 0b11110000, 0b00110100,  # Row 25
    0b00000111, 0b11001111, 0b11111000, 0b00100000,  # Row 26
    0b00000011, 0b11111111, 0b11111000, 0b00000000,  # Row 27
    0b00000000, 0b11111111, 0b11111111, 0b00000000,  # Row 28
    0b00000010, 0b00111111, 0b11111110, 0b01000000,  # Row 29
    0b00000000, 0b00001111, 0b11111000, 0b00000000,  # Row 30
    0b00000000, 0b00000000, 0b00000000, 0b00000000,  # Row 31
    0b00000000, 0b00000000, 0b00000000, 0b00000000,  # Row 32
]

LOLLIPOP_BITMAP = [
    0b00000000, 0b00000000, 0b00000000, 0b00000000,  # Row 1
    0b00000000, 0b00000000, 0b00011111, 0b00000000,  # Row 2
    0b00000000, 0b00000000, 0b11100000, 0b01100000,  # Row 3
    0b00000000, 0b00000001, 0b11000011, 0b00010000,  # Row 4
    0b00000000, 0b00000010, 0b10011000, 0b01101000,  # Row 5
    0b00000000, 0b00000101, 0b00100000, 0b00011100,  # Row 6
    0b00000000, 0b00000000, 0b01000111, 0b11001100,  # Row 7
    0b00000000, 0b00001010, 0b01001000, 0b00100110,  # Row 8
    0b00000000, 0b00001010, 0b00010111, 0b00010010,  # Row 9
    0b00000000, 0b00000000, 0b10011100, 0b10001010,  # Row 10
    0b00000000, 0b00000000, 0b10001100, 0b01001000,  # Row 11
    0b00000000, 0b00000010, 0b01000110, 0b00001000,  # Row 12
    0b00000000, 0b00000010, 0b01100110, 0b00001010,  # Row 13
    0b00000000, 0b00001001, 0b00011000, 0b01001010,  # Row 14
    0b00000000, 0b00001100, 0b10000010, 0b01001010,  # Row 15
    0b00000000, 0b00000110, 0b01111100, 0b10010100,  # Row 16
    0b00000000, 0b00000111, 0b00000001, 0b10010100,  # Row 17
    0b00000000, 0b00000110, 0b11000110, 0b00101000,  # Row 18
    0b00000000, 0b00001001, 0b00000000, 0b01110000,  # Row 19
    0b00000000, 0b00010010, 0b01000000, 0b11000000,  # Row 20
    0b00000000, 0b00100100, 0b00011111, 0b00000000,  # Row 21
    0b00000000, 0b01001000, 0b00000000, 0b00000000,  # Row 22
    0b00000000, 0b10010000, 0b00000000, 0b00000000,  # Row 23
    0b00000001, 0b00100000, 0b00000000, 0b00000000,  # Row 24
    0b00000010, 0b01000000, 0b00000000, 0b00000000,  # Row 25
    0b00000100, 0b10000000, 0b00000000, 0b00000000,  # Row 26
    0b00001001, 0b00000000, 0b00000000, 0b00000000,  # Row 27
    0b00010010, 0b00000000, 0b00000000, 0b00000000,  # Row 28
    0b00100100, 0b00000000, 0b00000000, 0b00000000,  # Row 29
    0b01001000, 0b00000000, 0b00000000, 0b00000000,  # Row 30
    0b00110000, 0b00000000, 0b00000000, 0b00000000,  # Row 31
    0b00000000, 0b00000000, 0b00000000, 0b00000000,  # Row 32
]









# LUT for full update
WS_20_30 = [                                    
    0x80,    0x66,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x40,    0x0,    0x0,    0x0,
    0x10,    0x66,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x20,    0x0,    0x0,    0x0,
    0x80,    0x66,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x40,    0x0,    0x0,    0x0,
    0x10,    0x66,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x20,    0x0,    0x0,    0x0,
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    0x14,    0x8,    0x0,    0x0,    0x0,    0x0,    0x2,                    
    0xA,    0xA,    0x0,    0xA,    0xA,    0x0,    0x1,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x14,    0x8,    0x0,    0x1,    0x0,    0x0,    0x1,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x1,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,    0x0,                    
    0x44,    0x44,    0x44,    0x44,    0x44,    0x44,    0x0,    0x0,    0x0,            
    0x22,    0x17,    0x41,    0x0,    0x32,    0x36
]


WF_PARTIAL_2IN9 = [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0A,0x0,0x0,0x0,0x0,0x0,0x1,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0xB0,0x32,0x36,
]

class EPD_2in9_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.partial_lut = WF_PARTIAL_2IN9
        self.full_lut = WS_20_30
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            self.delay_ms(10) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC7)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0x0F)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def lut(self, lut):
        self.send_command(0x32)
        self.send_data1(lut[0:153])
        self.ReadBusy()

    def SetLut(self, lut):
        self.lut(lut)
        self.send_command(0x3f)
        self.send_data(lut[153])
        self.send_command(0x03)     # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)     # source voltage
        self.send_data(lut[155])    # VSH
        self.send_data(lut[156])    # VSH2
        self.send_data(lut[157])    # VSL
        self.send_command(0x2c)        # VCOM
        self.send_data(lut[158])

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   

        self.send_command(0x01) #Driver output control      
        self.send_data(0x27)
        self.send_data(0x01)
        self.send_data(0x00)
    
        self.send_command(0x11) #data entry mode       
        self.send_data(0x07)

        self.SetWindow(0, 0, self.width-1, self.height-1)

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)
        self.send_data(0x80)
    
        self.SetCursor(0, 0)
        self.ReadBusy()

        self.SetLut(self.full_lut)
        # EPD hardware init end
        return 0

    def display(self, image):
        if (image == None):
            return            
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])   
        self.TurnOnDisplay()

    def display_Base(self, image):
        if (image == None):
            return   
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])    
                
        self.send_command(0x26) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])      
                
        self.TurnOnDisplay()

    def display_Partial(self, image):
        if (image == None):
            return
            
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(2)   
        self.SetLut(self.partial_lut)
        self.send_command(0x37) 
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00) 
        self.send_data(0x00)  
        self.send_data(0x40)  
        self.send_data(0x00)  
        self.send_data(0x00)   
        self.send_data(0x00)  
        self.send_data(0x00)
        self.send_command(0x3C) #BorderWaveform
        self.send_data(0x80)
        self.send_command(0x22) 
        self.send_data(0xC0)   
        self.send_command(0x20) 
        self.ReadBusy()
        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])    
        self.TurnOnDisplay_Partial()

    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        self.send_data1([color] * self.height * int(self.width / 8))
        self.send_command(0x26) # WRITE_RAM
        self.send_data1([color] * self.height * int(self.width / 8))
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            utime.sleep(1)
    print("Wi-Fi connected:", wlan.ifconfig()[0])


def fetch_all_address_info(addresses):
    total_balance = 0.0
    total_assets = {"SATORI": 0.0, "LOLLIPOP": 0.0}  # Initialize only the needed assets

    for address in addresses:
        attempt = 0  # Track retry attempts
        success = False
        while attempt < 3 and not success:  # Retry up to 3 times
            try:
                api_url = f"https://evr.cryptoscope.io/api/getaddress/?address={address}"
                response = urequests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    total_balance += float(data.get("balance", 0.0))

                    # Filter and aggregate only SATORI and LOLLIPOP
                    assets = data.get("assets", {})
                    for asset in ["SATORI", "LOLLIPOP"]:
                        if asset in assets:
                            try:
                                total_assets[asset] += float(assets[asset])
                            except ValueError:
                                print(f"Invalid value for {asset} in address {address}: {assets[asset]}")
                    success = True  # Mark as successful
                else:
                    print(f"Failed to fetch data for {address}. Status code: {response.status_code}")
            except Exception as e:
                print(f"Error fetching data for {address} (attempt {attempt + 1}):", e)
            finally:
                attempt += 1
                if not success and attempt < 3:
                    time.sleep(2)  # Wait for 2 seconds before retrying

    return {"balance": total_balance, "assets": total_assets}


class ScaledText:
    def __init__(self, framebuf, display_width):
        self.fb = framebuf
        self.display_width = display_width  # Use the actual display width

    def draw_bitmap(self, x, y, bitmap, width, height, color=0):
        """Draw a monochrome bitmap at a specified location."""
        for row in range(height):
            for col in range(width):
                bit = (bitmap[row * (width // 8) + (col // 8)] >> (7 - (col % 8))) & 0x01
                if bit:
                    self.fb.pixel(x + col, y + row, color)
                    
    def draw_scaled_text(self, text, x, y, scale=2, color=0):
        """Draw text with custom scaling factor.
        
        Args:
            text: String to display
            x: X coordinate
            y: Y coordinate
            scale: Integer scaling factor (default 2)
            color: Pixel color (0 or 1)
        """
        char_width = 8
        char_height = 8
        char_buf = bytearray(char_width * char_height)
        char_fb = framebuf.FrameBuffer(char_buf, char_width, char_height, framebuf.MONO_VLSB)
        
        cur_x = x
        for char in text:
            char_fb.fill(0)
            char_fb.text(char, 0, 0, 1)
            for cy in range(char_height):
                for cx in range(char_width):
                    if char_fb.pixel(cx, cy):
                        for sy in range(scale):
                            for sx in range(scale):
                                self.fb.pixel(
                                    cur_x + cx * scale + sx,
                                    y + cy * scale + sy,
                                    color
                                )
            cur_x += char_width * scale


    def center_text(self, text, y, scale=2, color=0):
        """Center text horizontally on the display."""
        char_width = 8
        text_width = len(text) * char_width * scale
        x = (self.display_width - text_width) // 2  # Use display width for centering
        self.draw_scaled_text(text, x, y, scale, color)

    def right_text(self, text, y, scale=2, color=0):
        """Align text to the right edge of the display."""
        char_width = 8
        text_width = len(text) * char_width * scale
        x = self.display_width - text_width  # Use display width for right alignment
        self.draw_scaled_text(text, x, y, scale, color)

def get_satori_avg_price():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        r = urequests.get("https://safe.trade/api/v2/trade/public/tickers/satoriusdt", headers=headers)
        
        if r.status_code == 200:
            data = r.json()
            avg_price = float(data['avg_price'])
            return avg_price
        else:
            return None
            
    except Exception as e:
        return None
    finally:
        r.close()  # Clean up the connection
        
def get_ntp_time():
    NTP_SERVER = "pool.ntp.org"
    NTP_PORT = 123
    NTP_DELTA = 2208988800  # seconds between 1900 and 1970
    
    # NTP request packet
    ntp_query = bytearray(48)
    ntp_query[0] = 0x1B  # Version 3, Mode 3 (client)
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        addr = socket.getaddrinfo(NTP_SERVER, NTP_PORT)[0][-1]
        sock.settimeout(2)
        sock.sendto(ntp_query, addr)
        msg = sock.recv(48)
        
        # Extract timestamp from response
        val = struct.unpack("!I", msg[40:44])[0]
        utc_time = val - NTP_DELTA
        
        # Adjust for timezone offset
        local_time = utc_time + TIMEZONE_GMT_OFFSET * 3600
        return local_time
    except:
        return None
    finally:
        sock.close()


def set_time():
    timestamp = None
    # Try up to 3 times to get NTP time
    for _ in range(3):
        timestamp = get_ntp_time()
        if timestamp is not None:
            break
        time.sleep(1)
    
    if timestamp is None:
        raise RuntimeError('Could not get NTP time')
    
    # Set RTC
    tm = time.gmtime(timestamp)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))

def main():
    connect_wifi()

        # Fetch data for all wallet addresses
    data = fetch_all_address_info(WALLET_ADDRESSES)
    if not data:
        print("Failed to fetch data. Exiting.")
        return

    # Parse the aggregated data
    evr_balance = data.get("balance", 0.0)
    assets = data.get("assets", {})
    print("Aggregated Assets:", assets)

    # Determine SATORI balance and price
    satori_balance = assets.get("SATORI", 0.0)
    satoriprice = get_satori_avg_price()

    # Initialize display
    epd = EPD_2in9_Landscape()
    epd.Clear(0xff)

    # Create scaled text handler
    text_handler = ScaledText(epd, EPD_WIDTH)
    epd.fill(1)

    # Display SATORI section
    text_handler.draw_scaled_text("SATORI", 30, 0, scale=3)
    #text_handler.draw_bitmap((128*2)+5, 0, SATORI_BITMAP, 32, 32)
    text_handler.draw_bitmap(0, 0, SATORI_BITMAP, 32, 32)
    
    text_handler.draw_scaled_text(f"{satori_balance:.2f}", 0, 40, scale=3)
    


    if satoriprice is not None:
        base_x = 200  # Base X-coordinate
        char_offset = 16  # Number of pixels to adjust per extra character
        satoriprice_str = str(satoriprice)  # Convert to string
        
        adjusted_x = base_x - (max(0, len(satoriprice_str) - 5) * char_offset)

        #text_handler.draw_scaled_text(f"${satoriprice}", 170, 0, scale=2)
        
        text_handler.draw_scaled_text(f"${satoriprice}", adjusted_x, 0, scale=2)
    else:
        text_handler.draw_scaled_text("Price N/A", 170, 30, scale=2)

    
    # Draw EVRMORE balance
    text_handler.draw_scaled_text(f"EVR: {evr_balance:.2f}", 0, 112-16-8, scale=2)
    #text_handler.draw_scaled_text(f"{evr_balance:.2f}", 140, y_offset, scale=2)

    # Add updated timestamp
    current_time = time.localtime()
    text_handler.draw_scaled_text("Updated: %02d:%02d %02d/%02d/%02d" % 
        (current_time[3], current_time[4], current_time[2], current_time[1], current_time[0] % 100), 0, 112, scale=1)

    # Draw version information ##PLACEHOLDERS##
    text_handler.draw_scaled_text("VER: v0.3.1 NEURONS: 19998 STAKE: 10", 0, 120 , scale=1)

    # Optional: Draw LOLLIPOP bitmap if present
    if "LOLLIPOP" in assets:
        text_handler.draw_bitmap(261, 86, LOLLIPOP_BITMAP, 32, 32)

    epd.display(epd.buffer)
    epd.sleep()

    print("Rebooting in 60 minutes...")
    time.sleep(3600)
    machine.reset()
    
if __name__ == "__main__":
    main()
