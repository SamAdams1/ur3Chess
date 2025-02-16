import socket

robotIP = "10.20.59.13"
PRIMARY_PORT = 30001
SECONDARY_PORT = 30002
REALTIME_PORT = 30003

new_line = "\n"

def send_urscript_command(command: str):
    """
    This function takes the URScript command defined above, 
    connects to the robot server, and sends 
    the command to the specified port to be executed by the robot.
    """
    try:
        print("Running command: ", command)
        # Create a socket connection with the robot IP and port number defined above
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((robotIP, PRIMARY_PORT))

        # Appends new line to the URScript command (the command will not execute without this)
        command = command+new_line
        
        # Send the command
        s.sendall(command.encode('utf-8'))
        
        # Close the connection
        # s.close()
        # s.recv () 1024 1108

        response = s.recv(2048)  # Increase buffer size
       
        # print(response.decode(errors='ignore'))
        print("No Error.")
    except Exception as e:
      print(f"An error occurred: {e}")


numbers = "12345678"
letters = "abcdefgh"
def squareInputLoop():
  while True:
    command = input("Enter newSquare (Example:'a1'):\n")
    newSquare = list(command)

    # go to IDLE before moving to squares or will cause joint errors
    # Word commands in try loop
    try: 
      match command:
        case "home":
          send_urscript_command("movej([-1.57,-1.57,0, -1.57,0,0], a=1.0, v=0.5, r=0.01)")
        case "idle":
          send_urscript_command("movej([-1.5589281,-1.424189,0.959931, -1.15192,-1.6350244,0], a=1.0, v=0.5, r=0.01)")
        case "boot":
          send_urscript_command("""
            if safetymode() == 3:
              power on
              robotmode active 
              unlock protective stop
              brake release
            end
          #   """)
        case "hello":
          send_urscript_command("set_digital_out(1, True)") 
        case "pose":
          send_urscript_command("textmsg(get_actual_tcp_pose())")

        case _:
          raise Exception()
        
    except:
      # Square commands in except loop
      # check input validity
      if newSquare[0] not in letters or newSquare[1] not in numbers:
        print("Invalid Square, IDIOT.\n\n")
      else:
        print("Moving to:", newSquare, "\n\n")
        calculateNewPos(newSquare)


def calculateNewPos(newSquare: list[str]):
  # change the letters into alphabet number index to perform math scaling operation
  # represents the difference in # of squares to the a1 square
  xScale = letters.index(newSquare[0])

  # subtract 1 to make 0, if a1 is enter it will go back to origin
  yScale = int(newSquare[1]) - 1 

  origin = [0.1375, 0.515] # square 'a1' coordinate points
  squareSize = 0.038

  newX = origin[0] - (squareSize * xScale)
  newY = origin[1] - (squareSize * yScale)

  send_urscript_command(f"movel(p[{newX}, {newY}, 0.03, -3.14,0,0], a=0.1, v=0.1, r=0)")

squareInputLoop()


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
pseudocode

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