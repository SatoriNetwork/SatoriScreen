import os
import machine

SETTINGS_FILE = "settings.txt"

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