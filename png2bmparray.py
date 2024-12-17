################################################################################
#                                                                              #
#  Script: PNG to Bitmap Converter                                             #
#  Description: Converts a PNG image to a binary bitmap array and provides     #
#               tools to output the bitmap as Python code or visualize it      #
#               using ASCII characters.                                        #
#                                                                              #
#  Usage: python script.py <image_path>                                        #
#  Args:                                                                       #
#      image_path (str): Path to the PNG image file.                           #
#                                                                              #
#  Features:                                                                   #
#      - Resizes and converts a PNG image to binary bitmap format.             #
#      - Outputs the bitmap as Python binary literals.                         #
#      - Visualizes the bitmap as ASCII art in the terminal.                   #
#                                                                              #
#  Author: https://github.com/JohnConnorNPC  X: @jc0839 Discord: @jc0839       #
#  License: MIT                                                                #
#  Version: 1.0                                                                #
#                                                                              #
################################################################################

import sys
from PIL import Image
import numpy as np

def png_to_bitmap_array(image_path, width=32, height=32):
    """
    Convert a PNG image to a bitmap array format.

    Args:
        image_path (str): Path to the PNG image.
        width (int): Desired width in pixels (default 32).
        height (int): Desired height in pixels (default 32).

    Returns:
        list: Bitmap array where each element represents a byte (8 bits).
    """
    # Open and resize the image
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    # Convert image pixels to binary (0 or 1) using a threshold
    pixels = np.array(img)
    pixels = (pixels < 128).astype(np.uint8)  # Threshold: 128

    # Convert binary pixels to a bitmap array
    bytes_per_row = (width + 7) // 8  # Round up to handle partial bytes
    bitmap = []

    for y in range(height):
        for byte_index in range(bytes_per_row):
            byte = 0
            for bit in range(8):
                x = byte_index * 8 + bit
                if x < width:  # Ensure we don't go out of bounds
                    byte |= pixels[y, x] << (7 - bit)
            bitmap.append(byte)

    return bitmap

def print_bitmap_as_code(bitmap, bytes_per_row=4):
    """
    Print the bitmap array as Python code with binary literals.

    Args:
        bitmap (list): List of bytes representing the bitmap.
        bytes_per_row (int): Number of bytes per row in the output.
    """
    print("BITMAP = [")
    for i in range(0, len(bitmap), bytes_per_row):
        row_bytes = bitmap[i:i + bytes_per_row]
        row_str = ", ".join(f"0b{byte:08b}" for byte in row_bytes)
        print(f"    {row_str},  # Row {i // bytes_per_row + 1}")
    print("]")

def visualize_bitmap(bitmap, width=32):
    """
    Visualize the bitmap using ASCII characters.

    Args:
        bitmap (list): List of bytes representing the bitmap.
        width (int): Width of the image in pixels.
    """
    bytes_per_row = (width + 7) // 8
    for i in range(0, len(bitmap), bytes_per_row):
        row = bitmap[i:i + bytes_per_row]
        bits = "".join(format(byte, '08b') for byte in row)
        print(''.join('#' if bit == '1' else '.' for bit in bits[:width]))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)

    IMAGE_PATH = sys.argv[1]
    WIDTH, HEIGHT = 32, 32  # Adjust image dimensions if needed

    # Generate bitmap array
    bitmap = png_to_bitmap_array(IMAGE_PATH, width=WIDTH, height=HEIGHT)

    # Output as Python code
    print("Bitmap as Python code:")
    print_bitmap_as_code(bitmap)

    # Visualize bitmap
    print("\nBitmap visualization:")
    visualize_bitmap(bitmap, width=WIDTH)



