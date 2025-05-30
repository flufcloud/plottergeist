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
bound_x1 = -0.156
bound_x2 = -0.443
bound_y1 = 0.271
bound_y2 = -0.295

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

            command = f'move{type}({pose}[{x}, {y}, {z}, {rx}, {ry}, {rz}])\n'
            print(command)

            print(f"Connected to socket, sending command")
            s.sendall(command.encode('utf-8'))

            time.sleep(7)

    except Exception as e:
        print(f"An error occured: {e}")     

def draw_bounding_box():
    # Move in a square shape and draw
    send_ur_script_command(f"movel(p[-0.156, 0.271, {Z}, {RX}, {RY}, {RZ}])")

    # Move in a square shape and draw
    send_ur_script_command(f"movel(p[-0.443, 0.271, {Z}, {RX}, {RY}, {RZ}])")

    # Move in a square shape and draw
    send_ur_script_command(f"movel(p[-0.443, -0.295, {Z}, {RX}, {RY}, {RZ}])")

    # Move to first point
    send_ur_script_command(f"movel(p[-0.156, -0.295, {Z}, {RX}, {RY}, {RZ}])")

def get_points_from_file(file_path : str):
    # This gets a list of (x,y) points from a target file 
    # (comma delimitted, no trailing new line). It automatically populates
    # the Z, RX, RY, and RZ values (it assumes you want to move the pen across the canvas).
    # It also sets the command to type pose and movel
    
    with open(file_path, 'r') as f:
        points = [[float(point.strip()) for point in line.split(',')] 
                + [Z, RX, RY, RZ, 'l', 'p'] for line in f]
    return points

print(f"Putting robot into default configuration")

# Move to home position
# DO NOT EDIT THESE COMMANDS

send_ur_script_command(0.0, -1.57, 0.0, -1.57, 0.0, 0.0, 'j', '')
send_ur_script_command(0.0, -1.04, 1.04, -1.57, -1.57, 0.0, 'j', '')

# ==========================

points = get_points_from_file('points.txt')
print(f"Begin drawing")

for point in points: send_ur_script_command(*point)

# return home
send_ur_script_command(0.0, -1.04, 1.04, -1.57, -1.57, 0.0, 'j', '')


# ==========================

"""
TODO:
    - Convert points into a pose so we can feed it to movel
    - Scale arbitrary points into our canvas space (linear scaling?)
    - Modify starting point to be first point on drawing (dynamic starting point)
    - Feed commands in a loop to hit all points on drawing
"""
