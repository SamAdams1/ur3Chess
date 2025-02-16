# old code that is no longer needed, for future reference


def saveRobotJointPos(square):
    try: 
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((robotIP, REALTIME_PORT))

      # Send the command
      command = "get_target_tcp_pose()" + new_line
      s.sendall(command.encode('utf-8'))
      
      data = s.recv(2048)  # Increase buffer size
      # print(data)
      print(f"Received data length: {len(data)} bytes")  # Debugging

      # Try different offsets
      offset = 252
      try:
          joint_positions = struct.unpack("!6d", data[offset:offset+48])  # 6 doubles (8 bytes each)
          print("command called:", command)
          print("returned:")
          print(f"{square} - Offset {offset}: {joint_positions}")
          # writeJointPos(square, joint_positions)
          
      except struct.error as e:
          print(f"Offset {offset} failed: {e}")
    except Exception as e:
      print(f"An error occurred: {e}")

def getPositionJSON():
  with open("./positions.json", "r", encoding="utf-8") as json_file:
    return json.load(json_file)

def writeJointPos(square, jointPos):
   positions = getPositionJSON()
   positions[square] = jointPos
  #  print(positions)

   with open(f"./positions.json", "w") as outfile:
    outfile.write(json.dumps(positions, indent=1))

def startRobot():
  send_urscript_command("""
    if safetymode() == 3:
      power on
      robotmode active 
      unlock protective stop
      brake release
    end
  #   """)
  # goes to the 'home' position where robot looking down at chess board
  send_urscript_command("movej(p[-0.17725,0.269777,0.326751,-2.79263,-0.857087,0.123928], a=1.0, v=0.5, r=0.01)")
