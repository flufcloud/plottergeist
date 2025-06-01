import socket
import time
import math
import enum

#initialize variables
robotIP = "192.168.56.101"
PRIMARY_PORT = 30001
INTERPERTER_PORT = 30020
Z = .0265
RX = 2.832
RY = -1.291
RZ = -0.0221

# x is vertical relative to the robot arm, decreasing x moves the pen up. decreasing y moves the pen left
bound_x1 = -0.256
bound_x2 = -0.448
bound_y1 = 0.271
bound_y2 = -0.295

def scale_and_translate_preserve_aspect(points, dest_top_left, dest_bottom_right):
    """Map original points into a destination rectangle, preserving aspect ratio"""
    # Get bounds of original
    xs = [x for x, y in points]
    ys = [y for x, y in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    shape_width = xmax - xmin
    shape_height = ymax - ymin

    x0, y0 = dest_top_left
    x1, y1 = dest_bottom_right
    box_width = x1 - x0
    box_height = y1 - y0

    # Uniform scale to fit in destination
    scale = min(box_width / shape_width, box_height / shape_height)

    # Center offset
    offset_x = x0 + (box_width - shape_width * scale) / 2
    offset_y = y0 + (box_height - shape_height * scale) / 2

    # Map points
    mapped = [
        (
            offset_x + (x - xmin) * scale,
            offset_y + (y - ymin) * scale
        )
        for x, y in points
    ]

    return mapped

"""
Pose: p[x, y, z, rx, ry, rz]
    - x, y, z are in meters
    - rx, ry, rz are in radians

Joint Angles: [j1, j2, j3, j4, j5, j6]
    - all angles are in radians

movej: moves the end effector into desired pose/angles
    - can take either pose or joint angles
    - does not move in linear motion, takes "optimal" path

movel: moves the end effector into desired pose/angles
    - can take either pose or joint angles
    - moves the end effector in linear motion, can cause issues because of this
    - use this command to draw lines
"""


def send_ur_script_command(x : float, y : float, z : float, rx : float, ry : float, rz : float, type : str, pose : str):
    # type = j for movej and l for movel
    # pose = '' for no pose and 'p' for pose
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Trying to connect to socket")
            s.connect((robotIP, PRIMARY_PORT))
            
            if type == 'l':
                a = 1.2
                v = 0.4
            else:
                a = 1.4
                v = 1.05
            command = f'move{type}({pose}[{x}, {y}, {z}, {rx}, {ry}, {rz}], a={a}, v={v})\n'
            print(command)

            print(f"Connected to socket, sending command")
            s.sendall(command.encode('utf-8'))

            time.sleep(3)

    except Exception as e:
        print(f"An error occured: {e}")     

def draw_bounding_box():
    # Move in a square shape and draw
    send_ur_script_command(bound_x1, bound_y1, Z, RX, RY, RZ, 'l', 'p')

    # Move in a square shape and draw
    send_ur_script_command(bound_x2, bound_y1, Z, RX, RY, RZ, 'l', 'p')

    # Move in a square shape and draw
    send_ur_script_command(bound_x2, bound_y2, Z, RX, RY, RZ, 'l', 'p')

    # Move to first point
    send_ur_script_command(bound_x1, bound_y2, Z, RX, RY, RZ, 'l', 'p')

    send_ur_script_command(bound_x1, bound_y1, Z, RX, RY, RZ, 'l', 'p')

def get_points_from_file(file_path : str):
    # This gets a list of (x,y) points from a target file 
    # (comma delimitted, no trailing new line). It automatically populates
    # the Z, RX, RY, and RZ values (it assumes you want to move the pen across the canvas).
    # It also sets the command to type pose and movel
    
    # Pull raw points
    with open(file_path, 'r') as f:
        points = [[float(point.strip()) for point in line.split(',')] 
               for line in f]

    # Transform
    points = scale_and_translate_preserve_aspect(points, (bound_x2, bound_y2), (bound_x1, bound_y1))

    # Pad with necessary data
    points = [
        [x, y, Z, RX, RY, RZ, 'l', 'p']
        for (x, y) in points
    ]

    return points

print(f"Putting robot into default configuration")

# Move to home position
# DO NOT EDIT THESE COMMANDS

send_ur_script_command(0.0, -1.57, 0.0, -1.57, 0.0, 0.0, 'j', '')


# ==========================

points = get_points_from_file('creature_points.txt')
print(f"Begin drawing")

len = len(points)
for i in range(len):
    if i % 5 == 0:
        print("Lifting pen")
        send_ur_script_command(0.0, -1.04, 1.04, -1.57, -1.57, 0.0, 'j', '')
    print(i) 
    send_ur_script_command(*points[i])

#draw_bounding_box()

# return home
send_ur_script_command(0.0, -1.04, 1.04, -1.57, -1.57, 0.0, 'j', '')


# ==========================