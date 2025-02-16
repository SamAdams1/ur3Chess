from robotConnection import rtde_c
from robotConnection import rtde_r
from robotConnection import vel
from robotConnection import acc

from robotActions import robotMoveSequence
from robotActions import board


#  attempt to move robot to home then idle when starting up
# try:
#   rtde_c.getActualTCPPose()
#   rtde_c.moveJ([-1.57,-1.57,0, -1.57,0,0], vel, acc)
#   rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc)
# except:
#   print('Start up movements failed.')


numbers = "12345678"
letters = "abcdefgh"

def humanInputLoop():
  while True:
    command = input("Enter Move(Example:'a1a2'):\n")
    newSquare = list(command)

    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
      match command:
        case "home":
          rtde_c.moveJ([-1.57,-1.57,0, -1.57,0,0], vel, acc)
        case "idle":
          rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc)
        case "pose":
          print("pose: ", rtde_c.getActualTCPPose())
        case _:
          raise Exception()
        
    except:
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers or newSquare[2] not in letters or newSquare[3] not in numbers :
        print("Invalid Square, IDIOT.\n\n")
      else:
        print("Moving to: ", newSquare[:2], newSquare[2:])

        # calculateNewPos(newSquare[:2], 'p')
        # calculateNewPos(newSquare[2:], 'd')

        # pushing humans move to board, then giving stockfish the boardstate
        board.push_san(command)
        # stockfish.set_fen_position(board.fen())
        # printBoard()

        robotMoveSequence()


humanInputLoop()

'''
        x,    y
a1: 0.1375, 0.515
a8: 0.1375, 0.2475
h8: -0.13, 0.2475
h1: -0.13, 0.515

add to z -> move robot up
add to  y -> move down number square 8 -> 1
add to x -> move up letter squares h -> a
'''

"""
pseudocode:

go above a1
go down
pick up piece
go up
go over to above desired square
go down
drop piece
click clock
return to idle
"""

"""
solve problem of not knowing if there is a piece already there when moving:

keep dictionary or 3d array of board state and check the array before moving
if there is a piece there, move it off the board before moving own piece!!
im smart

"""