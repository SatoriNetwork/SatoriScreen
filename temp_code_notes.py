# Notes for things I am adding in.
# ================================

# Read the onboard button, note: temporarily disables access to the external flash memory, temporarily disables interrupts and the other core to prevent them from trying to execute code from flash
# This cannot be run all the time.  Possibly flash led and pause for a couple of seconds on boot, and if it is pressed perform the update (which can call a seperate file entirely)
#import my_app
#my_app.main()

#Main app will need wifi & downloader for libraries.

import rp2
rp2.bootsel_button()


# Check for Missing Libraries and download them.  Or upgrade main.  Needs sanity checks.
# Might be able to have a number of libraries, and a simple main.py, and have it pull all the missing ones down, meaning user only has to copy over main.py, and update the settings via the serial console (or manually creating the file)

MAIN_FILE="https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/main.py"
REQUIRED_LIBRARIES = {
    "fonts": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/fonts.py",
    "bitmaps": "https://raw.githubusercontent.com/SatoriNetwork/SatoriScreen/refs/heads/main/bitmaps.py",
  
    }

def download_library(lib_name, url):
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            with open(f"{lib_name}.py", "wb") as f:
                f.write(response.content)
            print(f"Library '{lib_name}' downloaded successfully.")
        else:
            print(f"Failed to download '{lib_name}'. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading '{lib_name}': {e}")
      
def check_and_download_libraries():
    for lib, url in REQUIRED_LIBRARIES.items():
        try:
            __import__(lib)  # Try importing the library




# Globals to store settings, input by user, instead of being stored in the source code.  These changes will be needed with online updater.
WIFI_SSID = None
WIFI_PASSWORD = None
GMT_OFFSET = None
DATE_FORMAT = None
ADDRESSES = []

SETTINGS_FILE = "settings.txt"

def load_or_create_settings():
    global WIFI_SSID, WIFI_PASSWORD, GMT_OFFSET, DATE_FORMAT, ADDRESSES

    if SETTINGS_FILE in os.listdir():
        print("Settings file found. Loading...")
        with open(SETTINGS_FILE, "r") as file:
            lines = file.readlines()
            if len(lines) < 4:
                raise ValueError("Settings file is malformed. It must have at least 4 lines.")

            WIFI_SSID = lines[0].strip()
            WIFI_PASSWORD = lines[1].strip()
            GMT_OFFSET = int(lines[2].strip())
            DATE_FORMAT = lines[3].strip()
            ADDRESSES = [line.strip() for line in lines[4:]]

            print("Settings loaded successfully:")
            print(f"WIFI_SSID: {WIFI_SSID}")
            print(f"WIFI_PASSWORD: {WIFI_PASSWORD}")
            print(f"GMT_OFFSET: {GMT_OFFSET}")
            print(f"DATE_FORMAT: {DATE_FORMAT}")
            print(f"ADDRESSES: {ADDRESSES}")
    else:
        print("Settings file not found. Please provide the settings:")

        # Prompt user for input
        WIFI_SSID = input("Enter WiFi SSID: ").strip()
        WIFI_PASSWORD = input("Enter WiFi Password: ").strip()
        GMT_OFFSET = int(input("Enter GMT Offset (e.g., +10, -6): ").strip())
        DATE_FORMAT = input("Enter Date Format (dmy, ymd, mdy): ").strip().lower()

        ADDRESSES = []
        print("Enter addresses (one per line). Leave blank to finish:")
        while True:
            address = input().strip()
            if not address:
                break
            ADDRESSES.append(address)

        # Save settings to file
        print("Saving settings to file...")
        with open(SETTINGS_FILE, "w") as file:
            file.write(f"{WIFI_SSID}\n")
            file.write(f"{WIFI_PASSWORD}\n")
            file.write(f"{GMT_OFFSET}\n")
            file.write(f"{DATE_FORMAT}\n")
            for address in ADDRESSES:
                file.write(f"{address}\n")

        print("Settings saved successfully.")          
            print(f"Library '{lib}' is already installed.")
        except ImportError:
            print(f"Library '{lib}' not found. Downloading...")
            download_library(lib, url)


