from robotConnection import rtde_c
from robotConnection import rtde_r
from robotConnection import rtde_io
from robotConnection import vel
from robotConnection import acc

from robotActions import robotMoveSequence
from robotActions import board
from robotActions import calculateNewPos

import time

import keyboard

from robotActions import origin
squareSizeY = 0.0382
squareSizeX = 0.0385

def moveRobotWithKeyboard():
  # rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc)
  '''
    add to z -> move robot up
    add to  y -> move down number ~ square 8 -> 1
    add to x -> move up letter ~ squares h -> a
  '''

  safeX = 0.1375 
  safeY = 0.515
  safeZ = 0.3

  # x = -0.13 
  # y = 0.2475

  z = 0.03
  # z = 0.1

  
  while True:
    if keyboard.is_pressed("d"):
      origin[0] -= squareSizeX
    elif keyboard.is_pressed("a"):
      origin[0] += squareSizeX
    elif keyboard.is_pressed("w"):
      origin[1] -= squareSizeY
    elif keyboard.is_pressed("s"):
      origin[1] += squareSizeY
    elif keyboard.is_pressed("r"):
      z += 0.01
    elif keyboard.is_pressed("f"):
      z -= 0.01
    elif keyboard.is_pressed("q"):
      print(rtde_r.getActualTCPPose())
      time.sleep(0.5)

    rtde_c.moveL([origin[0], origin[1], z, -3.14,0,0], 0.05, 0.05)

# moveRobotWithKeyboard()

def squareSizeCalibrationTest():
  originCopy = origin

  for i in range(1,8):
    rtde_c.moveL([origin[0], origin[1], 0.03, -3.14,0,0], 0.05, 0.05)
    origin[0] -= squareSizeX

  for i in range(1,8):
    rtde_c.moveL([origin[0], origin[1], 0.03, -3.14,0,0], 0.05, 0.05)
    origin[1] -= squareSizeY
    


def moveToXPos():
  while True:
    x = float(input("Enter new X:"))

    # [0.13750777013424423, 0.5150145677723298, 0.03003519963260068, -3.1399216057739445, -9.682488007800743e-05, -0.0001103704880899726]
    rtde_c.moveL([x, 0.525, 0.03, -3.14,0,0], 0.05, 0.05)

def moveToYPos():
  while True:
    y = float(input("Enter new Y: "))

    # [0.13750777013424423, 0.5150145677723298, 0.03003519963260068, -3.1399216057739445, -9.682488007800743e-05, -0.0001103704880899726]
    rtde_c.moveL([0.1215, y, 0.03, -3.14,0,0], 0.05, 0.05)


# x = 0.1215
# Y:0.5125
# moveToYPos()
# moveToXPos()


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
          print("pose: ", rtde_r.getActualTCPPose())
        case "joint":
          print("jointPositions: ", rtde_r.getActualQ())
        case "close":
          try:
            status = rtde_io.setInputIntRegister(18, 1) 
            print(f"closing = Digital Input 18 State: {status}")
          except Exception as e:
            print(e)
        case "open":
          status = rtde_io.setInputIntRegister(18, 2) 
          print(f"opening - Digital Input 18 State: {status}")
        case "open":
          rtde_c.script("rq_open()")  # Open gripper
        case _:
          raise Exception()
        
    except:
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers or newSquare[2] not in letters or newSquare[3] not in numbers :
        print("Invalid Square, IDIOT.\n\n")
      else:
        print("Moving to: ", newSquare[:2], newSquare[2:])

        calculateNewPos(newSquare[:2], 'p')
        calculateNewPos(newSquare[2:], 'd')

        # pushing humans move to board
        board.push_san(command)
        # robots turn to move
        robotMoveSequence()

import threading

def playGame():
  # rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc) 

  # point to view chess board from top down.
  # rtde_c.moveJ([-1.9529297987567347, -1.3281212163022538, 0.5247171560870569, -1.320993722682335, -1.2840612570392054, -0.3136356512652796], vel, acc)
  # rtde_c.moveJ([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], vel, acc) 

  humanInputLoop()





playGame()

'''
        x,    y
a1: 0.1375, 0.515
a8: 0.1375, 0.2475
h8: -0.13, 0.2475
h1: -0.13, 0.515

captured pieces zone: (16 zones needed, cant capture king but extra queen)
[["","","","","",],
["","","","","",],
["","","","","",]]

add to z -> move robot up
add to  y -> move down number ~ square 8 -> 1 = file/row
add to x -> move down letter ~ squares h -> a = rank/col
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
cannot send script to robot as it stops the control script from running
will have to do the modbus solution


rtde_c.stopScript()
send tool closing script
rtde_c.reuploadScript()


"""