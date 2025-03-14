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
# board.set_board_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2") # test e4d5 pawn capture



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

  def readCommands(self, command):
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
      
  def receiveUserInput(self, command):
    newSquare = list(command)
    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
        self.readCommands(command)
    except:
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers:
        print("Invalid Square.\n")
      else:
        print("calculate:", command, "\n")
        self.moveSequence(command)

        board.push_san(command)
        self.robotDecisionMaking()


  def pickupOrDropSequence(self, pickupOrDrop: str, newX:float, newY: float, pieceZHeight: float):
    #moves down to table, pieces height
    time.sleep(2)
    self.moveL(newX, newY, pieceZHeight)
    time.sleep(2)
    
    match pickupOrDrop:
      case "pickup":
        self.closeGripper()
      case "drop":
        self.openGripper()
        
    time.sleep(2)
    self.moveL(newX, newY, pieceZHeight)
    time.sleep(2)


  def calculateNewSquareCoords(self, newSquare):
    origin = [0.1215, 0.5125] # square 'a1' center coordinate points [x, y]
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

    return [newX, newY]


  def moveSequence(self, move):
    # parsing algrebraic notation into two separate squares
    # need to catch special moves like castling and promoting a piece.
    pickupSquare = move[:2]
    dropSquare = move[2:]

    # x and y coordinate points of squares
    pickupCoords = self.calculateNewSquareCoords(pickupSquare)
    dropCoords = self.calculateNewSquareCoords(dropSquare)

    if len(move) == 4: # normal moves ex:'e2e4'
      # check if dropSquare is empty
      if board.piece_at(utils.chessFuncs.squareToNumber(dropSquare)):
        self.capturePiece(dropCoords)

      # go above the piece to be moved, then go down and pick it up
      self.moveL(pickupCoords[0], pickupCoords[1], 0.01)
      self.pickupOrDropSequence("pickup", pickupCoords[0], pickupCoords[1], -0.03)

      #move over to above the drop square, then go down and drop piece
      self.moveL(dropCoords[0], dropCoords[1], 0.01)
      self.pickupOrDropSequence("drop", dropCoords[0], dropCoords[1], -0.03)



    else: #castling, promotion, 
      print("abnormal move handling", move)

    printBoard()
    

  def capturePiece(self, pieceCoords):
    print("capturing piece at", pieceCoords)
    # move piece off board
    

  def robotDecisionMaking(self):
    # set stockfish board = pychess board then get bestmove
    stockfish.set_fen_position(board.fen())
    bestMove = stockfish.get_best_move()

    self.moveSequence(bestMove)
    board.push_san(bestMove)
    print(board.fen())
    print(bestMove)


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

# main()

def testPieceHeight(z):
  thisRobot = Robot()
  # z = -0.003
  MAX_Z = 0.05
  x, y = thisRobot.calculateNewSquareCoords("a1")
  # thisRobot.moveL(x, y, 0.0)
  # thisRobot.moveL(x, y, z)

  thisRobot.moveL(x, y, 0.0)
  time.sleep(.5)
  thisRobot.pickupOrDropSequence("pickup", x, y, z)
  time.sleep(1)
  thisRobot.moveL(x, y, MAX_Z)
  time.sleep(0.5)
  thisRobot.pickupOrDropSequence("drop", x, y, z)
  time.sleep(1)
  thisRobot.moveL(x, y, 0.0)

testPieceHeight(-0.05)

"""
calculate the z height to pick up pieces by indexing the dictionary


"""

# relative zheight - pawn, rook, knight, bishop, queen, king
pieceHeights = {
  "p": -0.05,
  "r": -0.04,
  "n": -0.04, #cannot pick up due to weird shape
  "b": -0.035,
  "q": -0.02,
  "k": -0.003, #very close/sketchy, hanging on by a thread
}
# 0.05 IS THE MAX HEIGHT FOR Z WITHOUT CAUSING JOINT FAILURES