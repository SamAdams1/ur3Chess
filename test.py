import socket
host = '192.168.56.1'
port = 50002         # Remains the same, because it is specified as default port in URCaps code
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall('GRIPPER_OPEN\n'.encode("utf-8"))
data = s.recv(1024)
s.close()
print('Received', repr(data))

"""
 rs485 is the protocol to communicate with the robots tool
"""

# import socket

# UR_IP = "10.20.59.13"  # Replace with your robot's IP
# PORT = 54321  # Tool Communication Forwarder Port

# # Example command to open the gripper (Modify based on gripper protocol)
# command = "GRIPPER_OPEN\n"

# # Connect to the robot's tool communication port
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((UR_IP, PORT))
# sock.sendall(command.encode("utf-8"))

# # Receive response (if applicable)
# response = sock.recv(1024)
# print("Received:", response.decode("utf-8"))

# sock.close()

