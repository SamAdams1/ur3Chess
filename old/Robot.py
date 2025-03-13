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

    self.a = "1.0" # robots max acceleration
    self.v = "0.5" # robots max velocity

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
      return self.socket.recv(2048)  # number is the buffer size
    else:
      print("Socket must be connected to send URScript." )

  def moveJ(self, jointPositions: str):
    self.sendUrScript(f"movej({jointPositions}, a={self.a}, v={self.v})")

  def moveL():
    {}
  
  # New Scale Precision Gripper
  def openGripper(self):
    print("open")
    with open("urScripts\openGripper.script", "r") as file:
      openScript = file.read()
    self.sendUrScript(openScript)
  
  def closeGripper(self):
    print("closing")
    with open("urScripts\closeGripper.script", "r") as file:
      closeScript = file.read()
    self.sendUrScript(closeScript)

  def receiveUserInput(self):
    command = input("Enter newSquare (Example:'a1'):\n")
    newSquare = list(command)

    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
      match command:
        case "home":
          self.moveJ("[-1.57,-1.57,0, -1.57,0,0]") # home
        case "idle":
          self.moveJ("[-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0]") # idle
        case "open":
          self.openGripper()
        case "close":
          self.closeGripper()
        # case "boot":
        #   send_urscript_command("""
        #     if safetymode() == 3:
        #       power on
        #       robotmode active 
        #       unlock protective stop
        #       brake release
        #     end
        #   #   """)
        # case "pose":
          # send_urscript_command("textmsg(get_actual_tcp_pose())")

        case _:
          raise Exception()
        
    except:
      return
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers:
        print("Invalid Square, IDIOT.\n\n")
      else:
        print("Moving to:", newSquare, "\n\n")
        calculateNewPos(newSquare)


def main():
  thisRobot = Robot()

  while True:
    thisRobot.receiveUserInput()

main()





    
