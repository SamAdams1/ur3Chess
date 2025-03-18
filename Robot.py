import socket
import utils
import time

new_line = "\n"
numbers = "12345678"
letters = "abcdefgh"
MAX_Z = 0.05

# for calculating square positions
origin = [0.1215, 0.5125] # square 'a1' center coordinate points [x, y]
squareSizeX = 0.0385
squareSizeY = 0.0382

# chess engine
from stockfish import Stockfish
stockfish = Stockfish(path=r"C:\Users\adams\Downloads\stockfish-windows-x86-64-vnni512\stockfish\stockfish-windows-x86-64-vnni512.exe")
stockfish.set_depth(20)
stockfish.set_elo_rating(1000)

# chess board
import chess
board = chess.Board()
# board.set_board_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR") # test e4d5 pawn capture
# board.set_board_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3KBNR") # White Queenside Castling
board.set_board_fen("1nbqkbnr/Pppppppp/8/8/8/8/1PPPPPPP/RNBQKBNR") # e7 pawn promoting


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

    # relative zheight - pawn, rook, knight, bishop, queen, king
    self.pieceHeights = { # 0.05 IS THE MAX HEIGHT FOR Z WITHOUT CAUSING JOINT FAILURES
      "p": -0.05,
      "r": -0.04,
      "n": -0.04, #cannot pick up due to weird shape
      "b": -0.035,
      "q": -0.02,
      "k": -0.003, #very close/sketchy, hanging on by a thread
    }

    self.whiteCaptureZone = [
      ["Q", "p", "", ""],
      ["", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""]
    ]
    self.blackCaptureZone = [
      ["q", "p", "", ""],
      ["", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""]
    ]

    self.turn = "White"


  def createSocket(self, port):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((self.ip, port))
  
      print(port, "Socket Connection Successful.")
      # self.goToIdle()
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
        self.goToIdle()
      case "open":
        self.openGripper()
      case "close":
        self.closeGripper()
      case _:
        raise Exception()
      
  def goToIdle(self):
    self.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0]) # idle
  

  def receiveUserInput(self, command: str):
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
        print("calculate:", command, new_line)
        self.moveSequence(command)
        board.push_san(command)
        printBoard()

        self.turn = "Black"
        self.robotDecisionMaking()


  def moveSequence(self, move):
    # parsing algrebraic notation into two separate squares
    # need to catch special moves like castling and promoting a piece.
    pickupSquare = move[:2]
    dropSquare = move[2:]

    # x and y coordinate points of squares
    pickupCoords = self.calculateSquareCoords(pickupSquare)
    dropCoords = self.calculateSquareCoords(dropSquare)

    if len(move) == 4: # normal moves ex:'e2e4'
      # check if dropSquare is empty
      pieceAtDropSquare = self.pieceAtSquare(dropSquare)
      if pieceAtDropSquare:
        self.capturePiece(dropCoords, pieceAtDropSquare)

      # returns letter abreviation of pieces
      pieceToPickup = self.pieceAtSquare(pickupSquare).lower()
      print(utils.chessFuncs.squareIndex[dropSquare], utils.chessFuncs.squareIndex[dropSquare])
      # go above the piece to be moved, then go down and pick it up
      self.pickupOrDropSequence("pickup", pickupCoords[0], pickupCoords[1], self.getPieceHeight(pieceToPickup))

      #move over to above the drop square, then go down and drop piece
      self.pickupOrDropSequence("drop", dropCoords[0], dropCoords[1], self.getPieceHeight(pieceToPickup))


    else: #castling, promotion, 
      print("abnormal move handling", move)

      # castling
      if "O-O" in move:
        self.castle(move)
      elif "x" in move:
        self.enPassant(move)
      elif len(move) == 5:
        self.promotionSequence(move)



  def pickupOrDropSequence(self, pickupOrDrop: str, newX:float, newY: float, pieceZHeight: float):
    time.sleep(2)
    # moves to above the desired square
    self.moveL(newX, newY, MAX_Z)
    time.sleep(2.5)
    #moves down to table, pieces height
    self.moveL(newX, newY, pieceZHeight)
    time.sleep(2)
    
    match pickupOrDrop:
      case "pickup":
        self.closeGripper()
      case "drop":
        self.openGripper()
        
    time.sleep(2)
    self.moveL(newX, newY, MAX_Z) # moves above squares
    time.sleep(.5)


  def calculateSquareCoords(self, newSquare):
    # change the letters into alphabet number index to perform math scaling operation
    # represents the difference in # of squares to the a1 square
    xScale = utils.chessFuncs.rankToNumber(newSquare[0])


    # subtract 1 to make 0, if a1 is enter it will go back to origin
    yScale = int(newSquare[1]) - 1
    # print("piece at:", newSquare, boardState[yScale][xScale])

    newX = origin[0] - (squareSizeX * xScale)
    newY = origin[1] - (squareSizeY * yScale)

    return [newX, newY]

  
  def pieceAtSquare(self, algNotation: str) -> str:
    piece = board.piece_at(utils.chessFuncs.squareIndex[algNotation])
    if piece:
      piece = piece.symbol()
    return piece


  # piece not yet lowered, white are still capital letters
  def capturePiece(self, pieceCoords: list[float], piece: str):
    pieceLowercase = piece.lower()
    print(f"capturing {piece} at", pieceCoords)

    self.pickupOrDropSequence("pickup", pieceCoords[0], pieceCoords[1], self.getPieceHeight(pieceLowercase))

    # move piece off board
    dropCoords = self.calculateCaptureZone(piece, "")
    self.pickupOrDropSequence("drop", dropCoords[0], dropCoords[1], self.getPieceHeight(pieceLowercase))

    # time.sleep(2)



  def calculateCaptureZone(self, piece:str, searchFor:str) -> list[float]:
    if piece.isupper():
      print("white", piece)

      xColScale, yRowScale = self.searchCaptureZone(self.whiteCaptureZone, piece, searchFor)

      # change default indexes
      xColScale += 9
      yRowScale += 3

      newX = origin[0] - (squareSizeX * xColScale)
      newY = origin[1] - (squareSizeY * yRowScale)

      return [newX, newY]
    
    if piece.islower():
      print("black", piece)

      xColScale, yRowScale = self.searchCaptureZone(self.blackCaptureZone, piece, searchFor)

      # change default indexes
      xColScale += 9 #white and black have same col index
      yRowScale += 7

      newX = origin[0] - (squareSizeX * xColScale)
      newY = origin[1] - (squareSizeY * yRowScale)

      return [newX, newY]
      
  # too search for empty spots in capture zone
  # col = rank, row = file
  def searchCaptureZone(self, captureZone: list[list[str]], piece: str, searchFor: str):
    for row in range(len(captureZone)):
      for col in range(len(captureZone[row])):
        if captureZone[row][col] == searchFor:
          print(row, col, captureZone[row][col])
          # if capturing set empty spot to piece, if promoting set to empty
          if captureZone[row][col] == "":
            captureZone[row][col] = piece
          else:
            captureZone[row][col] = ""

          print(captureZone)
          return col, row

  def getPieceHeight(self, pieceAbbrev) -> float:
    return self.pieceHeights[pieceAbbrev]
  
  def enPassant(self, move: str):
    print("en passant")

  def castle(self, move:str):
    if len(move) == 3:
      print(self.turn, "kingside castle")
    else:
      print(self.turn, "queenside castle")

  # A pawn moving from e7 to e8 and promoting to a queen would be notated as "e7e8q". 
  def promotionSequence(self, move:str):
    # ex: e7e8q -> e7 e8 q
    pickupSquare = move[:2]
    dropSquare = move[2:4]
    promoteTo = move [4:]

    pieceCoords = self.calculateSquareCoords(pickupSquare)
    piece = self.pieceAtSquare(pickupSquare)
    self.capturePiece(pieceCoords, piece)

    # coords of piece in capture zone to be used in promotion
    promoteToCoords = self.calculateCaptureZone(piece, promoteTo)
    self.pickupOrDropSequence("pickup", promoteToCoords[0], promoteToCoords[1], self.getPieceHeight(promoteTo.lower()))

    dropCoords = self.calculateSquareCoords(dropSquare)
    self.pickupOrDropSequence("drop", dropCoords[0], dropCoords[1], self.getPieceHeight(promoteTo.lower()))

    
    

  def promoteThisPiece(self, promoteTo: str):
    {}
    # search capture zone for piece, and pick up

  def robotDecisionMaking(self):
    # set stockfish board = pychess board then get bestmove
    stockfish.set_fen_position(board.fen())
    bestMove = stockfish.get_best_move()

    self.moveSequence(bestMove)
    board.push_san(bestMove)
    printBoard()
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
  printBoard()

  while True:
    thisRobot.turn = "White"
    command = input("Enter newSquare (Example:'e2e4'):\n")
    thisRobot.receiveUserInput(command)

# print(chess.B2, utils.chessFuncs.squareIndex["b2"])
main()

def testPieceHeight(z):
  thisRobot = Robot()
  # z = -0.003
  x, y = thisRobot.calculateSquareCoords("a1")
  # basic up and down, comment x,yz out when failure to adjust
  thisRobot.moveL(x, y, 0.0)
  thisRobot.moveL(x, y, z)

  # thisRobot.moveL(x, y, 0.0)
  # time.sleep(.5)
  # thisRobot.pickupOrDropSequence("pickup", x, y, z)
  # time.sleep(1)
  # thisRobot.moveL(x, y, MAX_Z)
  # time.sleep(0.5)
  # thisRobot.pickupOrDropSequence("drop", x, y, z)
  # time.sleep(1)
  # thisRobot.moveL(x, y, 0.0)

# testPieceHeight(-0.05)

"""
create functionality to:
 - castle kingside: O-O queenside: O-O-O
 - en passant
 - promote piece (put piece in capture zone, search capture zone for queen and put in old place of pawn)
 - promote and capture on same move
"""


