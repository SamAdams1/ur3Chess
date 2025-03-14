import socket
import utils
import time

new_line = "\n"
numbers = "12345678"
letters = "abcdefgh"

class Robot:
  def __init__(self):
    self.ip = "10.20.59.12"
    self.PRIMARY_PORT = 30001
    self.SECONDARY_PORT = 30002 # doubt i will use it
    self.REALTIME_PORT = 30003

    self.socket = self.createSocket(self.PRIMARY_PORT)
    self.realTimeSocket = self.createSocket(self.REALTIME_PORT)

    self.a = "0.3" # robots max acceleration
    self.v = "0.3" # robots max velocity


  def createSocket(self, port):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((self.ip, port))
  
      print(port, "Socket Connection Successful.")
      self.receiveUserInput("idle")
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

  def moveJ(self, jointPositions: list[float]):
    self.sendUrScript(f"movej({jointPositions}, a={self.a}, v={self.v})")

  def moveL(self, newX: float, newY: float, newZ: float):
    self.sendUrScript(f"movel(p[{newX}, {newY}, {newZ}, -3.14,0,0], a={self.a}, v={self.v})")
  
  def calculateZCoord(): # calc z coord based on height of the piece
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

  def receiveUserInput(self, command):
    newSquare = list(command)
    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
      match command:
        case "home":
          self.moveJ([-1.57,-1.57,0, -1.57,0,0]) # home
        case "idle":
          self.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0]) # idle
        case "open":
          self.openGripper()
        case "close":
          self.closeGripper()
        case _:
          raise Exception()
        
    except:
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers:
        print("Invalid Square.\n\n")
      else:
        print("Moving to:", newSquare, "\n\n")
        self.calculateNewPos(newSquare, "p")


  def calculateNewPos(self, newSquare: list[str], pickupDrop):
    #         x,      y
    origin = [0.1215, 0.5125] # square 'a1' center coordinate points
    squareSizeX = 0.0385
    squareSizeY = 0.0382
    
    # change the letters into alphabet number index to perform math scaling operation
    # represents the difference in # of squares to the a1 square
    xScale = utils.chessFuncs.fileToNumber(newSquare[0])


    # subtract 1 to make 0, if a1 is enter it will go back to origin
    yScale = int(newSquare[1]) - 1 
    # print("piece at:", newSquare, boardState[yScale][xScale])

    newX = origin[0] - (squareSizeX * xScale)
    newY = origin[1] - (squareSizeY * yScale)

    # z height which is above chess piece height
    safeZ = 0.01
    self.moveL(newX, newY, safeZ)
    time.sleep(2)
    # safeZ = self.calculateZCoord() 
    self.moveL(newX, newY, -0.075)

    match pickupDrop: #p for pickup, d for drop
      case "p":
        print("picking up piece")
        self.moveL(newX, newY, safeZ)
      case "d":
        print("dropping piece")
        self.moveL(newX, newY, safeZ)
        time.sleep(2)
        self.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0])


def main():
  thisRobot = Robot()

  while True:
    command = input("Enter newSquare (Example:'e2e4'):\n")

    thisRobot.receiveUserInput(command)

main()





    
