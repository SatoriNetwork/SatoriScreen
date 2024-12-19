import framebuf

class ScaledText:
    def __init__(self, framebuf, display_width):
        self.fb = framebuf
        self.display_width = display_width  # Use the actual display width

    def draw_bitmap(self, x, y, bitmap, width, height, color=0):
        """Draw a monochrome bitmap at a specified location."""
        bytes_per_row = (width + 7) // 8  # Handle any width, including non-multiples of 8

        for row in range(height):  # Iterate over each row
            for col in range(width):  # Iterate over each column
                byte_index = row * bytes_per_row + (col // 8)
                bit_index = 7 - (col % 8)

                # Extract the bit from the bitmap
                bit = (bitmap[byte_index] >> bit_index) & 0x01
                if bit:
                    self.fb.pixel(x + col, y + row, color)

    def draw_scaled_text(self, text, x, y, scale=2, color=0):
        """Draw text with custom scaling factor.

        Args:
            text: String to display
            x: X coordinate
            y: Y coordinate
            scale: Integer scaling factor (default 2)
            color: Pixel color (0 or 1)
        """
        char_width = 8
        char_height = 8
        char_buf = bytearray(char_width * char_height)
        char_fb = framebuf.FrameBuffer(char_buf, char_width, char_height, framebuf.MONO_VLSB)

        cur_x = x
        for char in text:
            char_fb.fill(0)
            char_fb.text(char, 0, 0, 1)
            for cy in range(char_height):
                for cx in range(char_width):
                    if char_fb.pixel(cx, cy):
                        for sy in range(scale):
                            for sx in range(scale):
                                self.fb.pixel(
                                    cur_x + cx * scale + sx,
                                    y + cy * scale + sy,
                                    color
                                )
            cur_x += char_width * scale