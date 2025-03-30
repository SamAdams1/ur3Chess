import socket
import utils
import time

new_line = "\n"
numbers = "12345678"
letters = "abcdefgh"
MAX_Z = 0.05

# for calculating square positions
origin = [0.1215, 0.509] # square 'a1' center coordinate points [x, y]
squareSizeX = 0.038
squareSizeY = 0.038

# chess engine
from stockfish import Stockfish
stockfish = Stockfish(path=r"C:\Users\adams\Downloads\stockfish-windows-x86-64-vnni512\stockfish\stockfish-windows-x86-64-vnni512.exe")
stockfish.set_depth(20)
stockfish.set_elo_rating(1000)


# chesster

# chess board
import chess
board = chess.Board()
# board.set_board_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR") # test e4d5 pawn capture
# board.set_board_fen("1nbqkbnr/Pppppppp/8/8/8/8/1PPPPPPP/RNBQKBNR") # e7 pawn promoting
# board.set_board_fen("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R") # Castling
# board.set_board_fen("3qkbn1/4p3/8/8/8/8/8/3QKBNR") # waiting for prints
board.set_board_fen("r7/1P6/8/8/8/8/8/8") # test simulataneous promotion and capture 



class Robot:
  def __init__(self):
    self.ip = "10.20.59.13"
    self.PRIMARY_PORT = 30001
    self.SECONDARY_PORT = 30002 # doubt i will use it
    self.REALTIME_PORT = 30003

    self.socket = self.createSocket(self.PRIMARY_PORT)
    self.realTimeSocket = self.createSocket(self.REALTIME_PORT)

    self.a = "0.7" # robots max acceleration
    self.v = "0.7" # robots max velocity

    self.turn = "White"
 
    # relative zheight - pawn, rook, knight, bishop, queen, king
    # self.pieceHeights = { # 0.05 IS THE MAX HEIGHT FOR Z WITHOUT CAUSING JOINT FAILURES
    #   "p": -0.05,
    #   "r": -0.04,
    #   "n": -0.04, #cannot pick up due to weird shape
    #   "b": -0.035,
    #   "q": -0.02,
    #   "k": -0.003, #very close/sketchy, hanging on by a thread
    # }
    self.pieceHeights = {
      "p": -0.024,
      "r": -0.024,
      "n": -0.024, 
      "b": -0.024,
      "q": -0.024,
      "k": -0.024, 
    }

    self.whiteCaptureZone = [
      ["Q", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""]
    ]
    self.blackCaptureZone = [
      ["q", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""],
      ["", "", "", ""]
    ]



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

  def moveJ(self, jointPositions: list[float]):
    self.sendUrScript(f"movej({jointPositions}, a={self.a}, v={self.v})")

  def moveL(self, newX: float, newY: float, newZ: float):
    self.sendUrScript(f"movel(p[{newX}, {newY}, {newZ}, -2.9, 1.25, 0], a={self.a}, v={self.v})")

    # self.sendUrScript(f"movel(p[{newX}, {newY}, {newZ}, -3.14,0,1], a={self.a}, v={self.v})")
    print(f"movel(p[{newX}, {newY}, {newZ}, -2.9, 1.25, 0], a={self.a}, v={self.v})")


  def toolPosition(self):
    self.sendUrScript(f"textmsg(get_actual_tcp_pose())")

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
      case "idle": # camera top position
        self.goToIdle()
      case "open":
        self.openGripper()
      case "close":
        self.closeGripper()
      case "view2":
        self.moveJ([-1.57,-1.57,0, -1.57,0,0])
      case "tool":
        self.toolPosition()

      case _:
        raise Exception()
      
  def goToIdle(self):
    # self.moveJ([-1.9529297987567347, -1.3281212163022538, 0.5247171560870569, -1.320993722682335, -1.2840612570392054, -0.3136356512652796]) # old
    # self.moveJ([-0.031365223278582405, 0.47343343710963476, 0.3452903986634218, -2.601733652973133, -0.010490056035830142, 0.031669042078009475]) # new
    self.moveJ([-1.90624861, -1.2788027, 0.50376348, -1.3528047, -1.3908529, -0.28363])

  def receiveUserInput(self, command: str):
    newSquare = list(command)
    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
        self.readCommands(command)
    except:
      # Square commands in except loop
      # check input validity
      # castling
      if "O-O" in command:
        self.castle(command)
      elif "x" in command:
        self.enPassant(command)
      elif len(command) == 5:
        self.promotionSequence(command)
      elif len(command) == 2:
        self.goToSquare(command)
      
      elif newSquare[0] not in letters or newSquare[1] not in numbers:
        print("Invalid Square.\n")
      else:
        print("calculate:", command, new_line)
        self.moveSequence(command)
        board.push_san(command)
        printBoard()

        self.turn = "Black"
        self.robotDecisionMaking()
        self.goToIdle()


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

      xColScale, yRowScale = self.searchCaptureZone(self.whiteCaptureZone, piece, searchFor.upper())

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
  
  # dxc6 - white d5 pawn captures black pawn on c5 by moving to c6
  def enPassant(self, move: str):
    # the piece capturing vs the piece being captured
    capturingPieceSquare = move[0]
    capturedPieceSquare = move[2]
    newFile = move[3]
    oldFile = int(newFile)

    # To find old file:White subtracts 1 from file as it moves up board numbers, black opposite.
    if self.turn == "White":
      oldFile -= 1
    else:
      oldFile += 1
    oldFile = str(oldFile)

    # behind the captured piece. on captured pieces file. either + or - captured pieces rank
    newSquare = capturedPieceSquare + newFile

    # d and c become d5, c5
    capturingPieceSquare += oldFile
    capturedPieceSquare += oldFile
    print(capturingPieceSquare, capturedPieceSquare, newFile, oldFile, newSquare)
    
    # move capturing piece to square behind the piece its taking.
    capturingPieceSquareCoords = self.calculateSquareCoords(capturingPieceSquare)
    newSquareCoords = self.calculateSquareCoords(newSquare)
    self.pickupOrDropSequence("pickup", capturingPieceSquareCoords[0], capturingPieceSquareCoords[1], self.getPieceHeight("p"))
    self.pickupOrDropSequence("drop", newSquareCoords[0], newSquareCoords[1], self.getPieceHeight("p"))

    # move en passanted piece off board
    capturedPieceSquareCoords = self.calculateSquareCoords(capturedPieceSquare)
    piece = "p"
    if self.turn == "White": # white needs uppercase P or will move to black capture zone.
      piece.upper()
    self.capturePiece(capturedPieceSquareCoords, piece)

    print("en passant")

  def castle(self, move:str):
    # self.turn = "Black"
    kingPickupCoords, kingDropCoords = self.kingCastleCoords(move)
    self.pickupOrDropSequence("pickup", kingPickupCoords[0], kingPickupCoords[1], self.getPieceHeight("p"))
    self.pickupOrDropSequence("drop", kingDropCoords[0], kingDropCoords[1], self.getPieceHeight("p"))
    
    rookPickupCoords, rookDropCoords = self.rookCastleCoords(move)
    self.pickupOrDropSequence("pickup", rookPickupCoords[0], rookPickupCoords[1], self.getPieceHeight("r"))
    self.pickupOrDropSequence("drop", rookDropCoords[0], rookDropCoords[1], self.getPieceHeight("r"))
    


  def kingCastleCoords(self, move:str):
    if len(move) == 3:
      print(self.turn, "kingside castle")
      if self.turn == "White":
        return [self.calculateSquareCoords("e1"), self.calculateSquareCoords("g1")]
      else: # black
        return [self.calculateSquareCoords("e8"), self.calculateSquareCoords("g8")]
    else:
      print(self.turn, "queenside castle")
      if self.turn == "White":
        return [self.calculateSquareCoords("e1"), self.calculateSquareCoords("c1")]
      else: # black
        return [self.calculateSquareCoords("e8"), self.calculateSquareCoords("c8")]


  def rookCastleCoords(self, move:str):
    if len(move) == 3:
      print(self.turn, "kingside castle")
      if self.turn == "White":
        return self.calculateSquareCoords("h1"), self.calculateSquareCoords("f1")
      else: # black
        return self.calculateSquareCoords("h8"), self.calculateSquareCoords("f8")
    else:
      print(self.turn, "queenside castle")
      if self.turn == "White":
        return self.calculateSquareCoords("a1"), self.calculateSquareCoords("d1")
      else: # black
        return self.calculateSquareCoords("a8"), self.calculateSquareCoords("d8")



  # A pawn moving from e7 to e8 and promoting to a queen would be notated as "e7e8q". 
  # capturing and promoting: "b7a8q"
  def promotionSequence(self, move:str):
    # ex: e7e8q -> e7 e8 q
    pickupSquare = move[:2]
    dropSquare = move[2:4]
    promoteTo = move [4:]

    print(pickupSquare, dropSquare, promoteTo)

    dropCoords = self.calculateSquareCoords(dropSquare)

    #if capturing move to capture zone
    pieceAtDropSquare = self.pieceAtSquare(dropSquare)
    if pieceAtDropSquare:
      self.capturePiece(dropCoords, pieceAtDropSquare)

    pieceCoords = self.calculateSquareCoords(pickupSquare)
    piece = self.pieceAtSquare(pickupSquare)
    self.capturePiece(pieceCoords, piece)

    # coords of piece in capture zone to be used in promotion
    promoteToCoords = self.calculateCaptureZone(piece, promoteTo)
    self.pickupOrDropSequence("pickup", promoteToCoords[0], promoteToCoords[1], self.getPieceHeight(promoteTo.lower()))

    # where placing promoted piece
    self.pickupOrDropSequence("drop", dropCoords[0], dropCoords[1], self.getPieceHeight(promoteTo.lower()))


  def goToSquare(self, square):
    squareCoords = self.calculateSquareCoords(square)

    if input("\nup or down\n") == "up":
      self.moveL(squareCoords[0], squareCoords[1], MAX_Z)
    else:
      self.moveL(squareCoords[0], squareCoords[1], self.pieceHeights["p"] + 0.001)
  
  def robotDecisionMaking(self):
    # set stockfish board = pychess board then get bestmove
    stockfish.set_fen_position(board.fen())
    bestMove = stockfish.get_best_move()

    self.moveSequence(bestMove)
    board.push_san(bestMove)
    printBoard()
    print(board.fen())
    print(bestMove)
  
  def testSquareCalib(self):
    # goes up through A rank then down the files to test if squares are perfectly calculated
    board.set_board_fen("8/8/8/8/8/8/8/R7") # waiting for prints

    curLetter = letters[0] # a
    i = 1
    while i < 8:
      move = curLetter + str(i) + curLetter + str(i+1)
      self.moveSequence(move)
      print(move)
      i += 1

    self.moveSequence("a8a1")

    for index, _ in enumerate(letters[:-1]):
      move = letters[index] + "1" + letters[index + 1] + "1"
      print(move)
      self.moveSequence(move)

    
      
def saveFen():
  with open("fen.txt", "w") as file:
    fen = board.fen().split(" ")[0]
    file.write(fen)

def getFen():
  try:
    f = open("fen.txt", "r")
    return f.read()
  except:
    print("No saved board fen.")

def printBoard():
  saveFen()

  print("   A B C D E F G H")
  print("   _______________")
  for rank, row in zip(range(8,0,-1), str(board).split("\n")):
      print(f"{rank} |{row}| {rank}")  # Add rank labels to each row
  print("   _______________")
  print("   A B C D E F G H")


def main():
  thisRobot = Robot()

  # get past fen incase of socket connection error
  fen = getFen()
  if fen:
    if input(f"\nResume past saved game?\n{fen}\ny - n\n") == "y":
      board.set_board_fen(fen)

  printBoard()

  # thisRobot.testSquareCalib()
  while True:
    thisRobot.turn = "White"
    command = input("Enter newSquare (Example:'e2e4'):\n")
    thisRobot.receiveUserInput(command)

main()

def testPieceHeight(z):
  thisRobot = Robot()
  x, y = thisRobot.calculateSquareCoords("a1")
  # basic up and down, comment x,yz out when failure to adjust
  thisRobot.moveL(x, y, 0.0)
  thisRobot.moveL(x, y, z)

# testPieceHeight(-0.025)
# testPieceHeight(0.05)

"""
create functionality to:
 - promote and capture on same move
 - move gripper lower when move across board with no piece in gripper

solve socket disconnecting problem

"""


