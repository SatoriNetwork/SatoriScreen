
"""
MicroPython SATORI & EVRMORE Wallet Monitor
=========================================

A MicroPython script that monitors wallet balances and displays data on a 2.9" ePaper display.
Fetches EVR balance, specific asset balances (SATORI, LOLLIPOP), and displays with custom visuals.

Features
--------
- Retrieves EVR balance and selected asset balances
- Fetches live SATORI price data
- Displays data on ePaper with custom visuals (bitmaps)
- Hourly updates with accurate NTP time
- Flexible text scaling and bitmap drawing tools

LED Status Codes
---------------
- Very Fast Blink: Ready for update (press bootsel button) first 5 sec after boot
- 0.5s on/off: Waiting to update screen (refresh attempted too early)
- 1.0s on/off: Normal operation - waiting for next screen update

    Author:        JC
    GitHub:        https://github.com/JohnConnorNPC
    X / Discord :  @jc0839
   

License: MIT

"""

# main.py

import time
import rp2
import network
import utime
import urequests
import machine
import os
import gc

NEEDS_UPDATE = False
try:
    # Project-specific imports
    from bitmaps import SATORI_BITMAP, LOLLIPOP_BITMAP, SATORI_LOGO
    from watchdog import Watchdog
    from scaled_text import ScaledText
    from epd_2in9_landscape import EPD_2in9_Landscape
    from ntp_client import NTPClient
    
    from display_service import DisplayService
    import arial10
    import arial_50
    import courier20
    import font10
    import font6
    import freesans20
except ImportError:
    NEEDS_UPDATE = True

# Constants
EPD_WIDTH = 128
EPD_HEIGHT = 296
UPDATE_INTERVAL = 300  # Minimum Screen update interval in seconds (Do not go below manufacturer spec)
LAST_UPDATE_FILE = "last_update.txt"
SETTINGS_FILE = "settings.txt"

# Required libraries for GitHub updates
REQUIRED_LIBRARIES = {
    "arial10": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/arial10.py",
    "arial_50": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/arial_50.py",
    "courier20": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/courier20.py",
    "font10": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/font10.py",
    "font6": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/font6.py",
    "freesans20": "https://raw.githubusercontent.com/waveshareteam/Pico_ePaper_Code/refs/heads/main/pythonNanoGui/gui/fonts/freesans20.py",
    "bitmaps": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/bitmaps.py",
    "watchdog": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/watchdog.py",
    "scaled_text": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/scaled_text.py",
    "epd_2in9_landscape": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/epd_2in9_landscape.py",
    "ntp_client": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/ntp_client.py",
    
    "display_service": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/display_service.py",
    "main": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/main.py",
}

def download_file(url, filename):
    try:
        print(f"Downloading {filename} from {url}...")
        response = urequests.get(url)
        gc.collect()
        if response.status_code == 200:
            with open(filename, 'w') as file:
                file.write(response.text)
            response=None
            gc.collect()
            print(f"Downloaded and saved {filename}.")
        else:
            print(f"Failed to download {filename}: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
    finally:
        response.close()
wlan = None
def connect_wifi(ssid, password, retries=20, delay=1):
    global wlan
    """Connect to WiFi network with retry mechanism."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("Already connected to Wi-Fi")
        return True

    wlan.connect(ssid, password)
    attempt = 0
    
    while not wlan.isconnected() and attempt < retries:
        print(f"WiFi connection attempt {attempt + 1}/{retries}")
        utime.sleep(delay)
        attempt += 1

    if wlan.isconnected():
        print("WiFi connected:", wlan.ifconfig()[0])
        return True
    print("Failed to connect to WiFi")
    return False

class LEDControl:
    def __init__(self, pin="LED"):
        """Initialize the LED on the specified pin."""
        self.led = machine.Pin(pin, machine.Pin.OUT)

    def turn_on(self):
        """Turn the LED on."""
        self.led.value(1)

    def turn_off(self):
        """Turn the LED off."""
        self.led.value(0)

    def blink(self, on_time, off_time):
        """Blink the LED once with specified ON and OFF durations."""
        self.turn_on()
        time.sleep(on_time)
        self.turn_off()
        time.sleep(off_time)

    def cleanup(self):
        """Clean up resources."""
        self.turn_off()
        del self.led

class Settings:
    def __init__(self):
        self.WIFI_SSID = None
        self.WIFI_PASSWORD = None
        self.GMT_OFFSET = None
        self.DATE_FORMAT = None
        self.ADDRESSES = []

    def validate_gmt_offset(self, value):
        try:
            offset = int(value)
            if -12 <= offset <= 14:
                return offset
            else:
                print("[Error] GMT Offset must be between -12 and +14.")
        except ValueError:
            print("[Error] GMT Offset must be an integer.")
        return None

    def validate_date_format(self, value):
        valid_formats = {"dmy", "ymd", "mdy"}
        if value in valid_formats:
            return value
        else:
            print("[Error] Date format must be one of 'dmy', 'ymd', or 'mdy'.")
        return None

    def prompt_yes_no(self, prompt):
        while True:
            response = input(f"{prompt} (yes/y or no/n): ").strip().lower()
            if response in {"yes", "y"}:
                return True
            elif response in {"no", "n"}:
                return False
            else:
                print("[Error] Invalid response. Please enter 'yes', 'y', 'no', or 'n'.")

    def load_or_create_settings(self):
        ascii_art_banner = """
╔════════════════════════════════════════════════════╗
║                                                    ║
║             Welcome to Satori Screen               ║
║                                                    ║
║              www.satorinet.io                      ║
║                                                    ║
╚════════════════════════════════════════════════════╝
        """
        print(ascii_art_banner)

        if SETTINGS_FILE in os.listdir():
            print("[OK] Settings file found. Loading...")
            with open(SETTINGS_FILE, "r") as file:
                lines = file.readlines()
                if len(lines) < 4:
                    raise ValueError("[Error] Settings file is malformed. It must have at least 4 lines.")

                self.WIFI_SSID = lines[0].strip()
                self.WIFI_PASSWORD = lines[1].strip()
                self.GMT_OFFSET = self.validate_gmt_offset(lines[2].strip())
                self.DATE_FORMAT = self.validate_date_format(lines[3].strip().lower())
                self.ADDRESSES = [line.strip() for line in lines[4:]]

                if self.GMT_OFFSET is None or self.DATE_FORMAT is None:
                    self.handle_invalid_settings()
                print("-----------------------------------------")
                print("[OK] Settings loaded successfully:")
                print(f"📡  WIFI_SSID: {self.WIFI_SSID}")
                print(f"🔑  WIFI_PASSWORD: {self.WIFI_PASSWORD}")
                print(f"🌍  GMT_OFFSET: {self.GMT_OFFSET}")
                print(f"📅  DATE_FORMAT: {self.DATE_FORMAT}")
                print(f"📍  ADDRESSES: {self.ADDRESSES}")
                print("-----------------------------------------")
                time.sleep(1)
                
        else:
            print("[Warning] Settings file not found. Please provide the settings:")

            self.WIFI_SSID = input("[Input] Enter WiFi SSID: ").strip()
            self.WIFI_PASSWORD = input("[Input] Enter WiFi Password: ").strip()

            while True:
                self.GMT_OFFSET = self.validate_gmt_offset(input("[Input] Enter GMT Offset (e.g., +10, -6): ").strip())
                if self.GMT_OFFSET is not None:
                    break

            while True:
                self.DATE_FORMAT = self.validate_date_format(input("[Input] Enter Date Format (dmy, ymd, mdy): ").strip().lower())
                if self.DATE_FORMAT is not None:
                    break

            self.ADDRESSES = []
            print("[Input] Enter addresses (one per line). Leave blank to finish:")
            while True:
                address = input("Address: ").strip()
                if not address:
                    break
                self.ADDRESSES.append(address)

            print("\n[Summary] Settings to be saved:")
            print("-----------------------------------------")
            print(f"📡  WIFI_SSID: {self.WIFI_SSID}")
            print(f"🔑  WIFI_PASSWORD: {self.WIFI_PASSWORD}")
            print(f"🌍  GMT_OFFSET: {self.GMT_OFFSET}")
            print(f"📅  DATE_FORMAT: {self.DATE_FORMAT}")
            print(f"📍  ADDRESSES: {self.ADDRESSES}")
            print("-----------------------------------------")

            if not self.prompt_yes_no("[Confirm] Save settings?"):
                print("[Warning] Settings not saved. Please restart the program to re-enter settings.")
                machine.reset()

            print("[OK] Saving settings to file...")
            with open(SETTINGS_FILE, "w") as file:
                file.write(f"{self.WIFI_SSID}\n")
                file.write(f"{self.WIFI_PASSWORD}\n")
                file.write(f"{self.GMT_OFFSET}\n")
                file.write(f"{self.DATE_FORMAT}\n")
                for address in self.ADDRESSES:
                    file.write(f"{address}\n")

            print("[OK] Settings saved successfully.")

    def handle_invalid_settings(self):
        print("[Error] Settings file contains invalid values. Deleting the file and rebooting...")
        try:
            if SETTINGS_FILE in os.listdir():
                os.remove(SETTINGS_FILE)
                print("[OK] Settings file deleted.")
            else:
                print("[Warning] Settings file does not exist, nothing to delete.")

            print("[Info] Rebooting the system...")
            machine.reset()
        except Exception as e:
            print(f"[Error] Failed to delete file or reboot: {e}")
            while True:
                pass

    def get_settings(self):
        """
        Return the loaded settings as a dictionary.
        """
        return {
            "WIFI_SSID": self.WIFI_SSID,
            "WIFI_PASSWORD": self.WIFI_PASSWORD,
            "GMT_OFFSET": self.GMT_OFFSET,
            "DATE_FORMAT": self.DATE_FORMAT,
            "ADDRESSES": self.ADDRESSES,
        }


class GitHubUpdater:
    def __init__(self, libraries):
        self.libraries = libraries

    def download_library(self, lib_name, url):
        try:
            print(f"Downloading library '{lib_name}' from {url}...")
            response = urequests.get(url)

            if response.status_code == 200 and response.content:
                temp_filename = f"{lib_name}.tmp"
                with open(temp_filename, "wb") as f:
                    f.write(response.content)
                response=None
                gc.collect()
                os.rename(temp_filename, f"{lib_name}.py")
                print(f"Library '{lib_name}' downloaded successfully.")
                time.sleep(1)
            else:
                print(f"Failed to download '{lib_name}'. HTTP Status Code: {response.status_code} or no content received.")
            gc.collect()
        except Exception as e:
            print(f"Error downloading '{lib_name}': {e}")
        finally:
            if 'response' in locals() and response:
                response.close()

    def check_and_download_libraries(self):
        for lib, url in self.libraries.items():
            if NEEDS_UPDATE:
             try:
                if os.stat(f"{lib}.py"):
                    continue
             except:
                 print(f"{lib}.py does not exist ")
            print(f"Library '{lib}' Downloading...")
            self.download_library(lib, url)
            try:
                __import__(lib)
                print(f"Library '{lib}' imported successfully after downloading.")
            except ImportError:
                print(f"Failed to import '{lib}' even after downloading.")

def save_last_update_time():
    try:
        with open(LAST_UPDATE_FILE, "w") as file:
            file.write(str(time.time()))
    except Exception as e:
        print(f"Error saving last update time: {e}")

def load_last_update_time():
    try:
        if LAST_UPDATE_FILE in os.listdir():
            with open(LAST_UPDATE_FILE, "r") as file:
                return float(file.read())
        return None
    except Exception as e:
        print(f"Error loading last update time: {e}")
        return None

def can_update_screen():
    last_update = load_last_update_time()
    if last_update is None:
        return True
        
    current_time = int(time.time())
    time_since_update = current_time - int(last_update)
    print(f"Current time: {current_time}")
    print(f"Time to wait: {UPDATE_INTERVAL - time_since_update:.1f}s before allowed to update screen")
    
    
    return time_since_update >= UPDATE_INTERVAL
if __name__ == "__main__":
    # Initialize components
    settings = Settings()
    settings.load_or_create_settings()

    
    try:
        # Load settings
        config = settings.get_settings()
        
        # Extract configuration
        WIFI_SSID = config["WIFI_SSID"]
        WIFI_PASSWORD = config["WIFI_PASSWORD"]
        GMT_OFFSET = config["GMT_OFFSET"]
        DATE_FORMAT = config["DATE_FORMAT"]
        ADDRESSES = config["ADDRESSES"]
        
        # Initialize LED control
        led = LEDControl()
        
        # Check for update mode
        led_on = True
        start_time = time.time()
        print("Checking for bootsel button press - Update mode")
        
        while time.time() - start_time < 5:
            led.turn_on() if led_on else led.turn_off()
            led_on = not led_on
            
            if rp2.bootsel_button() or NEEDS_UPDATE:
                if NEEDS_UPDATE:
                    if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
                        raise Exception("WiFi connection failed")
                print("Update mode activated")
                
                updater = GitHubUpdater(REQUIRED_LIBRARIES)
                updater.check_and_download_libraries()
                print("Update complete, rebooting...")
                led.turn_on()
                time.sleep(10)
                machine.reset()
            
            time.sleep(0.05)
        
        # Connect to WiFi for normal operation
        if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
            raise Exception("WiFi connection failed")
        print("WiFi Connected")
        
        # Initialize components
        watchdog = Watchdog()
        
        display_service = DisplayService(EPD_WIDTH, EPD_HEIGHT)
        watchdog.feed()
        
        # Set system time
        ntp_client = NTPClient(timezone_gmt_offset=GMT_OFFSET)
        ntp_client.set_time()
        
        led.turn_off()
        led_on = True

        while True:
            watchdog.feed()
            
            if can_update_screen():
                # Fetch all data using the display service
                
                balance_data = display_service.fetch_all_address_info(ADDRESSES, watchdog)
                
                gc.collect()
                neurons_data = display_service.fetch_neurons_data(watchdog)
                
                gc.collect()
                satori_price = display_service.get_satori_price(watchdog)
                
                gc.collect()
                
                
                
                # Initialize display
                watchdog.feed()
                epd = EPD_2in9_Landscape()
                text_handler = ScaledText(epd, EPD_WIDTH)
                    
                gc.collect()
                    
                # Update display using the display service
                display_service.update_display(epd, text_handler, balance_data, neurons_data, satori_price, watchdog, None)
                   
                watchdog.feed()
                epd.display(epd.buffer)
                epd.sleep()
                watchdog.feed()
                    
                # Save update time
                save_last_update_time()
                SECONDS_IN_HOUR = 3600
                counter = 0

                # Blink LED to indicate successful update
                
                #Low power mode.  19 MA vs ~150 ma while active
                wlan.active(False)
                wlan.disconnect()
                wlan.deinit()
                machine.freq(64000000)
                while True:
                    time.sleep(1)
                    counter += 1
                    led.turn_on() if led_on else led.turn_off()
                    led_on = not led_on
                    watchdog.feed()
                    if counter >= SECONDS_IN_HOUR:
                        machine.reset()
                        
            
            # Wait before next check
            time.sleep(0.5)
            led.turn_on() if led_on else led.turn_off()
            led_on = not led_on            
            
    except Exception as e:
        print(f"Runtime error: {e}")
        machine.reset()
    finally:
        watchdog.cleanup()
        led.cleanup()
