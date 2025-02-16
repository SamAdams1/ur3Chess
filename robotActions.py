
from stockfish import Stockfish
stockfish = Stockfish(path=r"C:\Users\adams\Downloads\stockfish-windows-x86-64-vnni512\stockfish\stockfish-windows-x86-64-vnni512.exe")
stockfish.set_depth(20)
stockfish.set_elo_rating(1000)

import chess
board = chess.Board()

from robotConnection import rtde_c
from robotConnection import rtde_r
from robotConnection import vel
from robotConnection import acc

import utils

# called after human moves
def robotMoveSequence():
  stockfish.set_fen_position(board.fen())
  bestMove = stockfish.get_best_move()
  board.push_san(bestMove)
  print(board.fen())
  print(bestMove)

  pickupSquare = bestMove[:2]
  dropSquare = bestMove[2:]

  # need square number not algrbreaic notation
  if board.piece_at(calcSquareNum(dropSquare)):
    print("capturing")
    calculateNewPos(dropSquare, 'p') # pickup captured piece


  calculateNewPos(pickupSquare, 'p')
  calculateNewPos(dropSquare, 'd')

  printBoard()






def calculateNewPos(newSquare: list[str], pickupDrop):
  # change the letters into alphabet number index to perform math scaling operation
  # represents the difference in # of squares to the a1 square
  xScale = utils.chessFuncs.fileToNumber(newSquare[0])


  # subtract 1 to make 0, if a1 is enter it will go back to origin
  yScale = int(newSquare[1]) - 1 
  # print("piece at:", newSquare, boardState[yScale][xScale])

  origin = [0.1375, 0.515] # square 'a1' coordinate points
  squareSize = 0.038

  newX = origin[0] - (squareSize * xScale)
  newY = origin[1] - (squareSize * yScale)

  safeZ = 0.1

  rtde_c.moveL([newX, newY, safeZ, -3.14,0,0], vel, acc)
  rtde_c.moveL([newX, newY, 0.03, -3.14,0,0], vel, acc)

  # move type
  match pickupDrop: #p for pickup, d for drop
    case "p":
      print("picking up piece")
      rtde_c.moveL([newX, newY, safeZ, -3.14,0,0], vel, acc)
    case "d":
      print("dropping piece")
      rtde_c.moveL([newX, newY, safeZ, -3.14,0,0], vel, acc)
      rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc)

def capturePiece():
  {}

def pickupPiece(square):
  {}
  
def putDownPiece(square):
  {}

def moveOffBoard():
  {}

def castle():
  {}
  # call move piece twice

# called after human moves to recognize their move and input it into virtual board
def analyzeBoardState():
  {}


def printBoard():
  print("   A B C D E F G H")
  print("   _______________")
  for rank, row in zip(range(8,0,-1), str(board).split("\n")):
      print(f"{rank} |{row}| {rank}")  # Add rank labels to each row
  print("   _______________")
  print("   A B C D E F G H")
  print("\n")

def robotRunLoop():
  {}
  # while True
  # takes picture every five seconds, waitng for human move
  # robot makes move: robotMoveSequence()
  # robot clicks clock
  # repeat
