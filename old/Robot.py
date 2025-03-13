import socket

new_line = "\n"


class Robot:

  def __init__(self):
    self.ip = "10.20.59.12"
    self.PRIMARY_PORT = 30001
    self.SECONDARY_PORT = 30002 # doubt i will use it
    self.REALTIME_PORT = 30003

    self.socket = self.createSocket(self.PRIMARY_PORT)
    self.realTimeSocket = self.createSocket(self.REALTIME_PORT)

  def createSocket(self, port):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((self.ip, port))
  
      print(port, "Socket Connection Successful.")
      return s
    except:
      print(f"Error: {port} Socket Didn't Connect.")

  
  def sendUrScript(self, URScript):
    URScript += new_line
    if self.socket:
      self.socket.sendall(URScript.encode('utf-8'))
      print("test")
      return self.socket.recv(2048)  # number is the buffer size
    else:
      print("Socket must be connected to send URScript.")

thisRobot = Robot()
thisRobot.sendUrScript("movej([-1.57,-1.57,0, -1.57,0,0], a=1.0, v=0.5, r=0.01)") # home: [-1.57,-1.57,0, -1.57,0,0]
    
