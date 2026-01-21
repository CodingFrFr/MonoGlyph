import time
import math
import os
import sys
from monoglyph import MonoGlyph



class Cube:
    def __init__(self, size):
        # Defined around (0,0,0)
        s = size / 2
        self.nodes = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ]
        self.edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]

    def rotate(self, angle_x, angle_y, angle_z):
        new_nodes = []
        cx, sx = math.cos(angle_x), math.sin(angle_x)
        cy, sy = math.cos(angle_y), math.sin(angle_y)
        cz, sz = math.cos(angle_z), math.sin(angle_z)

        for x, y, z in self.nodes:
            # Rotation X
            y, z = y * cx - z * sx, y * sx + z * cx
            # Rotation Y
            x, z = x * cy + z * sy, z * cy - x * sy
            # Rotation Z
            x, y = x * cz - y * sz, x * sz + y * cz
            new_nodes.append([x, y, z])
        return new_nodes

def main():
    angle = 0
    WIDTH, HEIGHT = 80, 40
    renderer = MonoGlyph(WIDTH, HEIGHT, '#')
    
    fps = 0
    prev_time = time.time()
    
    # Engine rotation is 0 (handle 3D rotation manually)
    renderer.set_rotation(0, WIDTH // 2, HEIGHT // 2)
    
    cube = Cube(size=15)
    
    # Camera State
    cam_x, cam_y, cam_z = 0, 0, -50
    angle_x, angle_y, angle_z = 0, 0, 0
    prev_buffer = None

    sys.stdout.write("\033[?25l") # Hide Cursor
    os.system('cls' if os.name == 'nt' else 'clear')
    print(renderer.color_char(renderer.logo, 120, 255, 210))
    print("Ctrl+C to Quit")
    
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        os.system('clear')
        print('You quit to early.')
        return


    try:
        while True:
                renderer.clear(renderer.color_char(renderer.get_shade(0.8), 0, 0, 0))
                
                r = int(127 + 127 * math.sin(math.radians(angle)))
                g = int(127 + 127 * math.sin(math.radians(angle + 120)))
                b = int(127 + 127 * math.sin(math.radians(angle + 240)))
                

                # Rotate Cube
                rotated_nodes = cube.rotate(angle_x, angle_y, angle_z)
                
                # Project to 2D (with Camera Offset)
                projected_points = []
                focal_length = 60
                
                for x, y, z in rotated_nodes:
                    # Camera Transform
                    rel_x = x - cam_x
                    rel_y = y - cam_y
                    rel_z = z - cam_z  # Distance from camera
                    
                    # Avoid division by zero (clipping)
                    if rel_z <= 0.1: 
                        rel_z = 0.1
                        
                    factor = focal_length / rel_z
                    
                    # Projection + Screen Center Offset
                    px = int(rel_x * factor + WIDTH / 2)
                    py = int(rel_y * factor * 0.5 + HEIGHT / 2)
                    projected_points.append((px, py))

                # Draw Edges
                for p1, p2 in cube.edges:
                    x0, y0 = projected_points[p1]
                    x1, y1 = projected_points[p2]

                    shade_z = 1 - (rel_z / 100) # To chose the 'shade' of the cube
                    renderer.draw_line(x0, y0, x1, y1, renderer.get_shade(shade_z), r, g, b)
                
                # renderer.draw_text(0, 0, f"FPS: {fps:.2f}")
                # Render
                #renderer.render()
                renderer.render_delta(prev_buffer)
                prev_buffer = [row[:] for row in renderer.buffer]
                
                angle_x += 0.05
                angle_y += 0.03
                
                time.sleep(0.015)
                
                current_time = time.time()
                    
                # Calculate the time elapsed since the last frame
                time_elapsed = current_time - prev_time
                
                # Calculate FPS: 1 frame / time elapsed
                if time_elapsed > 0: # Avoid division by zero
                    fps = 1 / time_elapsed
                    
                
                # Update previous time for the next iteration
                prev_time = current_time
                
                angle += 2
                
    except KeyboardInterrupt:
        os.system('clear')
        sys.stdout.write("\033[?25h") # Restore Cursor
        print("Exited.")

if __name__ == "__main__":
    main()
