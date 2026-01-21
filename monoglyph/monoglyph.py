import sys
import math


class MonoGlyph:
    SHADE_CHARS = ".:-=+*#%@"


    def __init__(self, width: int, height: int, default_char: str = " "):
        self.width = width
        self.height = height
        self.default_char = default_char
        self.buffer = [[default_char for _ in range(width)] for _ in range(height)]
        self.current_angle = 0.0
        self.origin_x = 0
        self.origin_y = 0
        self.logo = """
         __  __                   ____  _    //       _
        |  \/  | ___  _ __   ___ / ___|| |_ ""_ _ __ | |__
        | |\/| |/ _ \| '_ \ / _ \| |  _| | | | | '_ \| '_  \ 
        | |  | | (_) | | | | (_) | |_| | | |_| | |_)|| | | |
        |_|  |_|\___/|_| |_|\___/ \____|_|\__, | .__/|_| |_|
                                          |___/|_|
        """ # Logo is for demos/examples; not needed in actual uses


    def set_rotation(self, degrees: float, origin_x: int = 0, origin_y: int = 0):
        """Sets the rotation angle and point."""
        self.current_angle = math.radians(degrees)
        self.origin_x = origin_x
        self.origin_y = origin_y


    def get_shade(self, intensity: float) -> str:
        """Maps 0.0 to 1.0 to a shaded character."""
        clamped = max(0.0, min(1.0, intensity))
        if clamped <= 0.0:
           return self.default_char
        idx = int(clamped * (len(self.SHADE_CHARS) - 1))
        return self.SHADE_CHARS[idx]


    def color_char(self, char: str, r: int, g: int, b: int) -> str:
        """Returns ANSI escape code for an rgb value"""
        return f"\x1b[38;2;{r};{g};{b}m{char}\x1b[0m"


    def _plot(self, x: int, y: int, char: str, r: int = None, g: int = None, b: int = None):
        """Raw pixel writer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if r is not None and g is not None and b is not None:
                char = self.color_char(char, r, g, b)
            self.buffer[y][x] = char


    def rotate_point(self, x: int, y: int):
        """Applies current rotation to a point2d."""
        if self.current_angle == 0:
            return round(x), round(y)

        # Translate to local space (relative to pivot)
        temp_x = x - self.origin_x
        temp_y = y - self.origin_y

        # 2D Rotation Matrix
        cos_a = math.cos(self.current_angle)
        sin_a = math.sin(self.current_angle)

        rotated_x = temp_x * cos_a - temp_y * sin_a
        rotated_y = temp_x * sin_a + temp_y * cos_a

        # Translate back to world space and round to integer
        return round(rotated_x + self.origin_x), round(rotated_y + self.origin_y)

    def set_pixel(self, x: int, y: int, char: str, r: int = None, g: int = None, b: int = None):
        """Rotates a single pixel."""
        rx, ry = self.rotate_point(x, y)
        self._plot(rx, ry, char, r, g, b)


    # DRAWING


    def draw_line(self, x0: int, y0: int, x1: int, y1: int, char: str, r: int = None, g: int = None, b: int = None):
        # Rotate the vertices, run only twice
        start_x, start_y = self.rotate_point(x0, y0)
        end_x, end_y = self.rotate_point(x1, y1)


        # Bresenham's Algorithm
        dx = abs(end_x - start_x)
        dy = -abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        err = dx + dy


        while True:
            self._plot(start_x, start_y, char, r, g, b)
            if start_x == end_x and start_y == end_y:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                start_x += sx
            if e2 <= dx:
                err += dx
                start_y += sy


    def draw_rect(self, x: int, y: int, width: int, height: int, char: str, r: int = None, g: int = None, b: int = None):
        # Top
        self.draw_line(x, y, x + width - 1, y, char, r, g, b)
        # Bottom
        self.draw_line(x, y + height - 1, x + width - 1, y + height - 1, char, r, g, b)
        # Left
        self.draw_line(x, y, x, y + height - 1, char, r, g, b)
        # Right
        self.draw_line(x + width - 1, y, x + width - 1, y + height - 1, char, r, g, b)


    def draw_triangle(self, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int, char: str, r: int = None, g: int = None, b: int = None):
        self.draw_line(x0, y0, x1, y1, char, r, g, b)
        self.draw_line(x1, y1, x2, y2, char, r, g, b)
        self.draw_line(x2, y2, x0, y0, char, r, g, b)


    def draw_circle(self, xc: int, yc: int, radius: int, char: str, r: int = None, g: int = None, b: int = None):
        # Rotation only affects the center position for a circle
        cx, cy = self.rotate_point(xc, yc)

        x = 0
        y = radius
        d = 3 - 2 * radius


        def _plot_circle_points(cx, cy, x, y, char, r, g, b):
            self._plot(cx + x, cy + y, char, r, g, b)
            self._plot(cx - x, cy + y, char, r, g, b)
            self._plot(cx + x, cy - y, char, r, g, b)
            self._plot(cx - x, cy - y, char, r, g, b)
            self._plot(cx + y, cy + x, char, r, g, b)
            self._plot(cx - y, cy + x, char, r, g, b)
            self._plot(cx + y, cy - x, char, r, g, b)
            self._plot(cx - y, cy - x, char, r, g, b)


        _]plot_circle_points(cx, cy, x, y, char, r, g, b)
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            _plot_circle_points(cx, cy, x, y, char, r, g, b)


    def draw_text(self, x: int, y: int, text: str, r: int = None, g: int = None, b: int = None):
        for i, char in enumerate(text):
            self.set_pixel(x + i, y, char, r, g, b)


    # FILLED DRAWING


    def _draw_horizontal_line(self, x_start: int, x_end: int, y: int, char: str, r: int = None, g: int = None, b: int = None):
        if x_start > x_end:
            x_start, x_end = x_end, x_start
        for x in range(max(0, x_start), min(self.width, x_end + 1)):
            self._plot(x, y, char, r, g, b)


    def fill_rect(self, x: int, y: int, width: int, height: int, char: str, r: int = None, g: int = None, b: int = None):
        """Fills rect. Handles rotation through triangles."""
        # Vertices: TopLeft, TopRight, BottomRight, BottomLeft
        x0, y0 = x, y
        x1, y1 = x + width - 1, y
        x2, y2 = x + width - 1, y + height - 1
        x3, y3 = x, y + height - 1


        # Split into 2 triangles: (TL, TR, BL) and (TR, BR, BL)
        # This reuses the rotation logic in fill_triangle automatically
        self.fill_triangle(x0, y0, x1, y1, x3, y3, char, r, g, b)
        self.fill_triangle(x1, y1, x2, y2, x3, y3, char, r, g, b)


    def fill_triangle(self, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int, char: str, r: int = None, g: int = None, b: int = None):
        """Standard triangle fill method."""
        # Rotate vertices first
        x0, y0 = self.rotate_point(x0, y0)
        x1, y1 = self.rotate_point(x1, y1)
        x2, y2 = self.rotate_point(x2, y2)


        # Sort by Y coordinate (y0 <= y1 <= y2)
        if y0 > y1: x0, y0, x1, y1 = x1, y1, x0, y0
        if y0 > y2: x0, y0, x2, y2 = x2, y2, x0, y0
        if y1 > y2: x1, y1, x2, y2 = x2, y2, x1, y1


        def _interp(y, y_start, y_end, x_start, x_end):
            if y_start == y_end:
                return x_start
            return x_start + (x_end - x_start) * (y - y_start) / (y_end - y_start)


        # Draw flat-bottom part
        for y in range(int(y0), int(y1)):
            sx = _interp(y, y0, y2, x0, x2)
            ex = _interp(y, y0, y1, x0, x1)
            self._draw_horizontal_line(int(sx), int(ex), y, char, r, g, b)


        # Draw flat-top part
        for y in range(int(y1), int(y2) + 1):

            sx = _interp(y, y0, y2, x0, x2)
            ex = _interp(y, y1, y2, x1, x2)
            self._draw_horizontal_line(int(sx), int(ex), y, char, r, g, b)
 
 
    def fill_circle(self, xc: int, yc: int, radius: int, char: str, r: int = None, g: int = None, b: int = None):
        cx, cy = self.rotate_point(xc, yc)
       
        # Scanline fill
        for dy in range(-radius, radius + 1):
            # Width at this height
            dx = int(math.sqrt(radius**2 - dy**2))
            self._draw_horizontal_line(cx - dx, cx + dx, cy + dy, char, r, g, b)
 
    # UTIL
 
    def clear(self, char: str = None):
        for y in range(self.height):
            for x in range(self.width):
                if not char:
                    self.buffer[y][x] = self.default_char
                else:
                    self.buffer[y][x] = char
 
 
    def render(self):
        print('\033[H', end='')  # ANSI Home Cursor
        sys.stdout.write('\n'.join(''.join(row) for row in self.buffer) + '\n')
 
 
    def render_delta(self, prev_buffer: list[list[str]] | None) -> None:
        """Render only characters that changed from prev frame."""
        if (
            prev_buffer is None or
            len(prev_buffer) != self.height or
            any(len(row) != self.width for row in prev_buffer)
        ):
            # Fallback: full render
            self.render()
            return
    
        output: list[str] = []
        for y in range(self.height):
            for x in range(self.width):
                char = self.buffer[y][x]
                if prev_buffer[y][x] != char:
                    output.append(f"\033[{y + 1};{x + 1}H{char}")

    if output:
        sys.stdout.write("".join(output))
        sys.stdout.flush()
