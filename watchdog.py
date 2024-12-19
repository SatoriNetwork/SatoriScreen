import machine
import gc
import time
import os

class Watchdog:
    """
    A simple Watchdog Timer (WDT) implementation for MicroPython.
    """

    def __init__(self, timeout=8388):
        """
        Initialize the Watchdog Timer.

        Args:
            timeout (int): The timeout value in milliseconds (default: 8388ms).
        """
        self._nowatchdog_cached = self._nowatchdog_file_exists()
        self.enabled = not self._nowatchdog_cached
        if self.enabled:
            self.wdt = machine.WDT(timeout=timeout)
            print("NOWATCHDOG file not found. Watchdog is enabled.")
        else:
            print("NOWATCHDOG file found. Watchdog is disabled.")

    def _nowatchdog_file_exists(self):
        """
        Check if the NOWATCHDOG file exists in the filesystem.

        Returns:
            bool: True if the NOWATCHDOG file exists, False otherwise.
        """
        return "NOWATCHDOG" in os.listdir()

    def feed(self):
        """
        Feed the Watchdog Timer to prevent a reset.
        """
        if self.enabled:
            self.wdt.feed()

    def cleanup(self):
        """
        Clean up the Watchdog Timer.
        When using the IDE, this will stop the watchdog and allow the ide to control the RP2040 without the watchgod rebooting it.
        """
        if self.enabled:
            del self.wdt
            gc.collect()
            self.enabled = False
            # Stop/disable the RP2040 watchdog timer
            # 0x40058000 = WATCHDOG_CTRL register, bit 30 is the ENABLE bit. from the 2040 datasheet.
            machine.mem32[0x40058000] = machine.mem32[0x40058000] & ~(1<<30)

