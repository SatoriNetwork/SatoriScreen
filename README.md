# SatoriScreen

A MicroPython-based wallet monitor for SATORI and EVRMORE that displays balance information on a 2.9" ePaper screen.

![SatoriScreen Display](https://github.com/user-attachments/assets/2dd0aa0c-9475-4713-9e83-1dfcc2ac9d4a)
![Hardware Setup](https://github.com/user-attachments/assets/a9ccd19b-12fa-40ab-a175-4300ae388b45)

## Features

### Current Implementation
- WiFi connectivity
- Multiple wallet address monitoring (SATORI & EVR balances)
- NTP time synchronization
- Display of:
  - Satori & EVR balances
  - Update time
  - Neuron count
  - Satori Price
  - Software version display
  - Current stake information
- Watchdog implementation
- Onboard LED status indicators (WiFi, Updates, Operation)
- Screen refresh protection system
- Direct GitHub upgrade/install capability

## Hardware Requirements

**Important:** Use the RPI Pico W (wireless version). RPI Pico 2 W should be compatible but is untested.

### International Suppliers
- **Display:** [Waveshare Pico ePaper 2.9](https://www.waveshare.com/pico-epaper-2.9.htm)
- **Microcontroller:** [Raspberry Pi Pico WH](https://www.waveshare.com/raspberry-pi-pico-w.htm?sku=23104)

### Australian Suppliers
- **Display:** [Waveshare Pico ePaper 2.9](https://core-electronics.com.au/waveshare-2-9inch-e-paper-module-for-raspberry-pi-pico-296x128-black-white.html)
- **Microcontroller:** [Raspberry Pi Pico WH](https://core-electronics.com.au/raspberry-pi-pico-wh.html)

## Installation Guide

### Initial Setup
1. If using a new RPI Pico W, install the full MicroPython firmware:
   - Follow [Getting Started with Pico - Step 2](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2)
   - Continue with [Getting Started with Pico - Step 3](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3)

### Software Installation
1. Launch Thonny IDE
2. Create a new file or clear existing content
3. Copy contents from `main.py` into the editor
4. Save as `main.py` on the Raspberry Pi Pico
5. Run the script:
   - Automatic: Click play in Thonny and follow prompts to download required libraries
   - Manual: Create individual library files listed in REQUIRED_LIBRARIES

### Hardware Assembly
Connect the RPI Pico to the Waveshare screen:
- Align USB port with ribbon cable side
- Ensure both components face upward (text visible)
- Reference Image 2 for correct orientation
- Follow Manufacturer Instructions

## Utility Scripts

### png2bmparray.py
Converts PNG images to bitmap arrays for display compatibility

### main.py
Primary script containing core functionality

## License
MIT
