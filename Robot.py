import socket
import utils
import time

new_line = "\n"
numbers = "12345678"
letters = "abcdefgh"

from stockfish import Stockfish
stockfish = Stockfish(path=r"C:\Users\adams\Downloads\stockfish-windows-x86-64-vnni512\stockfish\stockfish-windows-x86-64-vnni512.exe")
stockfish.set_depth(20)
stockfish.set_elo_rating(1000)

import chess
board = chess.Board()

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

  
  def openGripper(self): # New Scale Precision Gripper
    with open("urScripts\openGripper.script", "r") as file:
      openScript = file.read()
    self.sendUrScript(openScript)

  def closeGripper(self): # New Scale Precision Gripper
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
        print("calculate:", command, "\n")
        self.calculateNewPos(newSquare, "p")
        self.calculateNewPos(newSquare[2:], "d")

        board.push_san(command)
        printBoard()
        self.robotMoveSequence()


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
    time.sleep(1)


    match pickupDrop: #p for pickup, d for drop
      case "p":
        print("picking up piece")
        self.closeGripper()
        time.sleep(2)
        self.moveL(newX, newY, safeZ)
        time.sleep(2)
      case "d":
        print("dropping piece")
        self.openGripper()
        time.sleep(2)
        self.moveL(newX, newY, safeZ)
        time.sleep(2)
        self.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0])
        time.sleep(2)

  
  def robotMoveSequence(self):
    stockfish.set_fen_position(board.fen())
    bestMove = stockfish.get_best_move()
    board.push_san(bestMove)
    print(board.fen())
    print(bestMove)

    pickupSquare = bestMove[:2]
    dropSquare = bestMove[2:]

    # checks dropOff square is empty
    if board.piece_at(utils.chessFuncs.squareToNumber(dropSquare)):
      print("capturing")
      self.calculateNewPos(dropSquare, 'p') # pickup captured piece

    self.calculateNewPos(pickupSquare, 'p')
    self.calculateNewPos(dropSquare, 'd')
    
    

    printBoard()

def printBoard():
  print("   A B C D E F G H")
  print("   _______________")
  for rank, row in zip(range(8,0,-1), str(board).split("\n")):
      print(f"{rank} |{row}| {rank}")  # Add rank labels to each row
  print("   _______________")
  print("   A B C D E F G H")
  print("\n")


def main():
  thisRobot = Robot()

  while True:
    command = input("Enter newSquare (Example:'e2e4'):\n")

    thisRobot.receiveUserInput(command)

main()





    
