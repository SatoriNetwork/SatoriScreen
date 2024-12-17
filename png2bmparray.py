import argparse
from PIL import Image
import numpy as np

def png_to_bitmap_array(image_path, width=None, height=None, invert=False):
    """
    Convert a PNG image to a bitmap array format using its original dimensions by default.
    
    Args:
        image_path (str): Path to the PNG image
        width (int): Desired width in pixels (default None, uses image's width)
        height (int): Desired height in pixels (default None, uses image's height)
        invert (bool): Whether to invert pixel colors (default False)
    
    Returns:
        list: Bitmap array where each element represents a byte (8 bits)
    """
    # Open image and get original size
    img = Image.open(image_path)
    img = img.convert('L')  # Convert to grayscale
    
    # Use original image dimensions if width and height are not provided
    original_width, original_height = img.size
    width = width or original_width
    height = height or original_height

    # Resize only if dimensions are explicitly specified
    if (width, height) != img.size:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert to numpy array and threshold
    pixels = (np.array(img) < 128).astype(np.uint8)  # Threshold at 128
    
    if invert:
        pixels = 1 - pixels  # Invert the binary pixel values
    
    # Initialize bitmap array
    bytes_per_row = (width + 7) // 8
    bitmap = []
    
    # Convert pixels to bitmap array
    for y in range(height):
        for byte_index in range(bytes_per_row):
            byte = 0
            for bit in range(8):
                x = byte_index * 8 + bit
                if x < width:
                    byte |= pixels[y, x] << (7 - bit)
            bitmap.append(byte)
    
    return bitmap, width, height  # Return dimensions for verification

def print_bitmap_as_code(bitmap, bytes_per_row=4):
    """
    Print bitmap as Python code with binary literals.
    
    Args:
        bitmap (list): List of bytes representing the bitmap
        bytes_per_row (int): Number of bytes per row in the output
    """
    print("BITMAP = [")
    for i in range(0, len(bitmap), bytes_per_row):
        row_bytes = bitmap[i:i + bytes_per_row]
        row_str = ", ".join(f"0b{byte:08b}" for byte in row_bytes)
        print(f"    {row_str},  # Row {i // bytes_per_row + 1}")
    print("]")

def visualize_bitmap(bitmap, width):
    """
    Visualize the bitmap using ASCII characters.
    
    Args:
        bitmap (list): List of bytes representing the bitmap
        width (int): Width of the image in pixels
    """
    bytes_per_row = (width + 7) // 8
    for i in range(0, len(bitmap), bytes_per_row):
        row = bitmap[i:i + bytes_per_row]
        bits = ""
        for byte in row:
            bits += format(byte, '08b')
        print(''.join('#' if bit == '1' else '.' for bit in bits[:width]))

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert PNG image to a bitmap array.")
    parser.add_argument("image_path", type=str, help="Path to the PNG image.")
    parser.add_argument("--width", type=int, default=None, help="Optional width to resize the image.")
    parser.add_argument("--height", type=int, default=None, help="Optional height to resize the image.")
    parser.add_argument("--invert", action="store_true", help="Invert pixel colors.")
    args = parser.parse_args()

    # Process image and generate bitmap
    bitmap, width, height = png_to_bitmap_array(args.image_path, args.width, args.height, args.invert)
    
    # Display results
    print(f"Image dimensions: {width}x{height}\n")
    
    print("Bitmap as Python code:")
    print_bitmap_as_code(bitmap)
    
    print("\nBitmap visualization:")
    visualize_bitmap(bitmap, width)
