# SatoriScreen

![image](https://github.com/user-attachments/assets/a2d10989-8b8e-4036-b0c5-07a056c22910)
![image](https://github.com/user-attachments/assets/a9ccd19b-12fa-40ab-a175-4300ae388b45)

## Hardware Requirements
The Waveshare screen comes with soldered terminals; you can purchase unsoldered or pre-soldered RPI Pico versions. **Make sure to use the RPI Pico W (wireless version).** The RPI Pico 2 W should also work, though it has not been tested.

International
- **Screen:** [Waveshare Pico ePaper 2.9](https://www.waveshare.com/pico-epaper-2.9.htm)
- **RPI Pico WH:** [Raspberry Pi Pico W](https://www.waveshare.com/raspberry-pi-pico-w.htm?sku=23104)

Australia
- **Screen:** [Waveshare Pico ePaper 2.9](https://core-electronics.com.au/waveshare-2-9inch-e-paper-module-for-raspberry-pi-pico-296x128-black-white.html)
- **RPI Pico W:** [Raspberry Pi Pico WH](https://core-electronics.com.au/raspberry-pi-pico-wh.html)



---
## Software Overview
The software is currently a **Work in Progress (WIP)**. The following features are implemented:

- Connects to WiFi.
- Retrieves **SATORI** and **EVR** balances from multiple wallet addresses.
- Fetches current time via **NTP**.
- Displays balance and time on the ePaper screen.

### Upcoming Features
Additional APIs are needed to display:
- Software version.
- Neuron count.
- Current stake.

---
## Scripts

### `png2bmparray.py`
Used to create bitmap arrays for loading into the screen code.

### `main.py`
Main script to be loaded onto the RPI Pico W.

---
## Installation & Setup

### Installing or Updating the Code on the RPI Pico W
1. Open **Thonny** (a Python IDE).
2. Paste the code from `main.py` into the editor.
    - If an existing file opens, click **New**.
3. Edit the following variables at the top of the file:
    - **WiFi details** (SSID and password).
    - **Wallet addresses**.
    - **GMT Offset**.
    - **Date format**.
4. Go to **File > Save As**.
5. Select **Raspberry Pi Pico** as the destination.
6. Save the file as `main.py`.

---
## Hardware Installation
The RPI Pico plugs directly into the Waveshare screen:
- The **USB port** on the Pico must align with the same side as the **ribbon cable**.
- The text on both the Pico and the screen should face **upwards**.

Refer to Image 2 above for clarity.

---
## Loading Firmware on a New RPI Pico W
Out of the box, the RPI Pico W may not have the required **full firmware** for MicroPython. Follow these steps to load it:

1. [Getting Started with Pico - Step 2](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2)
2. [Getting Started with Pico - Step 3](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3)

---
### License
MIT
