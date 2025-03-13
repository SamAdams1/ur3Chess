import socket

HOST = "192.168.1.10"  # Replace with robot's IP
PORT = 30002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))

command = "movej([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], a=0.5, v=0.5)\n"  # Example command

s.sendall(command.encode('utf-8')) #encode to utf8
