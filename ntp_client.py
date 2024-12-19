import socket
import struct
import time
import machine

class NTPClient:
    def __init__(self, ntp_server="pool.ntp.org", timezone_gmt_offset=0):
        self.NTP_SERVER = ntp_server
        self.NTP_PORT = 123
        self.NTP_DELTA = 2208988800  # seconds between 1900 and 1970
        self.TIMEZONE_GMT_OFFSET = timezone_gmt_offset

    def get_ntp_time(self):
        """Retrieve the current time from an NTP server."""
        ntp_query = bytearray(48)
        ntp_query[0] = 0x1B  # Version 3, Mode 3 (client)

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            addr = socket.getaddrinfo(self.NTP_SERVER, self.NTP_PORT)[0][-1]
            sock.settimeout(2)
            sock.sendto(ntp_query, addr)
            msg = sock.recv(48)

            # Extract timestamp from response
            val = struct.unpack("!I", msg[40:44])[0]
            utc_time = val - self.NTP_DELTA

            # Adjust for timezone offset
            local_time = utc_time + self.TIMEZONE_GMT_OFFSET * 3600
            return local_time
        except:
            return None
        finally:
            sock.close()

    def set_time(self):
        """Set the RTC with the current time from an NTP server."""
        timestamp = None

        # Try up to 3 times to get NTP time
        for _ in range(5):
            timestamp = self.get_ntp_time()
            if timestamp is not None:
                break
            time.sleep(1)

        if timestamp is None:
            raise RuntimeError('Could not get NTP time')

        # Set RTC
        tm = time.gmtime(timestamp)
        utc_time_str = f"{tm[0]:04}-{tm[1]:02}-{tm[2]:02} {tm[3]:02}:{tm[4]:02}:{tm[5]:02} UTC"
        local_time = time.localtime(timestamp + self.TIMEZONE_GMT_OFFSET * 3600)
        local_time_str = f"{local_time[0]:04}-{local_time[1]:02}-{local_time[2]:02} {local_time[3]:02}:{local_time[4]:02}:{local_time[5]:02} Local"
        print("UTC Time:", utc_time_str)
        print("Local Time:", local_time_str)


        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
 