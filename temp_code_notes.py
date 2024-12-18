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
            print(f"Library '{lib}' is already installed.")
        except ImportError:
            print(f"Library '{lib}' not found. Downloading...")
            download_library(lib, url)
            try:
                # Attempt to import the library after downloading
                __import__(lib)
                print(f"Library '{lib}' imported successfully after downloading.")
            except ImportError:
                print(f"Failed to import '{lib}' even after downloading.")





# Globals to store settings, input by user, instead of being stored in the source code.  These changes will be needed with online updater.
WIFI_SSID = None
WIFI_PASSWORD = None
GMT_OFFSET = None
DATE_FORMAT = None
AUTO_UPDATE = None
ADDRESSES = []

SETTINGS_FILE = "settings.txt"

def validate_gmt_offset(value):
    try:
        offset = int(value)
        if -12 <= offset <= 14:
            return offset
        else:
            print("Error: GMT Offset must be between -12 and +14.")
    except ValueError:
        print("Error: GMT Offset must be an integer.")
    return None

def validate_date_format(value):
    valid_formats = {"dmy", "ymd", "mdy"}
    if value in valid_formats:
        return value
    else:
        print("Error: Date format must be one of 'dmy', 'ymd', or 'mdy'.")
    return None

def validate_auto_update(value):
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    else:
        print("Error: Auto Update must be 'True' or 'False'.")
    return None
    
def load_or_create_settings():
    global WIFI_SSID, WIFI_PASSWORD, GMT_OFFSET, DATE_FORMAT, AUTO_UPDATE, ADDRESSES

    if SETTINGS_FILE in os.listdir():
        print("Settings file found. Loading...")
        with open(SETTINGS_FILE, "r") as file:
            lines = file.readlines()
            if len(lines) < 5:
                raise ValueError("Settings file is malformed. It must have at least 5 lines.")

            WIFI_SSID = lines[0].strip()
            WIFI_PASSWORD = lines[1].strip()
            GMT_OFFSET = validate_gmt_offset(lines[2].strip())
            DATE_FORMAT = validate_date_format(lines[3].strip().lower())
            AUTO_UPDATE = validate_auto_update(lines[4].strip().lower())
            ADDRESSES = [line.strip() for line in lines[5:]]

            if GMT_OFFSET is None or DATE_FORMAT is None or AUTO_UPDATE is None:
                handle_invalid_settings()


            print("Settings loaded successfully:")
            print(f"WIFI_SSID: {WIFI_SSID}")
            print(f"WIFI_PASSWORD: {WIFI_PASSWORD}")
            print(f"GMT_OFFSET: {GMT_OFFSET}")
            print(f"DATE_FORMAT: {DATE_FORMAT}")
            print(f"AUTO_UPDATE: {AUTO_UPDATE}")
            print(f"ADDRESSES: {ADDRESSES}")
    else:
        print("Settings file not found. Please provide the settings:")

        # Prompt user for input
        WIFI_SSID = input("Enter WiFi SSID: ").strip()
        WIFI_PASSWORD = input("Enter WiFi Password: ").strip()
        
        while True:
            GMT_OFFSET = validate_gmt_offset(input("Enter GMT Offset (e.g., +10, -6): ").strip())
            if GMT_OFFSET is not None:
                break

        while True:
            AUTO_UPDATE = validate_auto_update(input("Auto Update (True/False): ").strip())
            if AUTO_UPDATE is not None:
                break

        while True:
            DATE_FORMAT = validate_date_format(input("Enter Date Format (dmy, ymd, mdy): ").strip().lower())
            if DATE_FORMAT is not None:
                break

        ADDRESSES = []
        print("Enter addresses (one per line). Leave blank to finish:")
        while True:
            address = input().strip()
            if not address:
                break
            ADDRESSES.append(address)

        # Print settings and ask for confirmation
        print("\nSettings to be saved:")
        print(f"WIFI_SSID: {WIFI_SSID}")
        print(f"WIFI_PASSWORD: {WIFI_PASSWORD}")
        print(f"GMT_OFFSET: {GMT_OFFSET}")
        print(f"DATE_FORMAT: {DATE_FORMAT}")
        print(f"AUTO_UPDATE: {AUTO_UPDATE}")
        print(f"ADDRESSES: {ADDRESSES}")

        confirm = input("\nConfirm save? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Settings not saved. Please restart the program to re-enter settings.")
            machine.reset()
            

        # Save settings to file
        print("Saving settings to file...")
        with open(SETTINGS_FILE, "w") as file:
            file.write(f"{WIFI_SSID}\n")
            file.write(f"{WIFI_PASSWORD}\n")
            file.write(f"{GMT_OFFSET}\n")
            file.write(f"{DATE_FORMAT}\n")
            file.write(f"{'true' if AUTO_UPDATE else 'false'}\n")
            for address in ADDRESSES:
                file.write(f"{address}\n")

        print("Settings saved successfully.")

def handle_invalid_settings():
    print("Error: Settings file contains invalid values. Deleting the file and rebooting...")
    try:
        # Delete the settings file
        if SETTINGS_FILE in os.listdir():
            os.remove(SETTINGS_FILE)
            print("Settings file deleted.")
        else:
            print("Settings file does not exist, nothing to delete.")

        # Reboot the system
        print("Rebooting the system...")
        machine.reset()
    except Exception as e:
        print(f"Failed to delete file or reboot: {e}")
        # In case of failure, halt the execution
        while True:
            pass
