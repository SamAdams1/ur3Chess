How to use this repo:

Required tools:
* Git
* Python
* pip
* Stockfish chess engine
* IDE of choice

Program:
0. Install the above dependencies if you do not already have them.
1. Git clone this repo into your desired directory.
2. In the "Robot.py" file, replace the Stockfish path to the path of your own Stockfish installation.
3. If not already installed run: "pip install socket time chess"
4. Program is ready to run.

Robot Connection:
1. Plug in the LAN network to an outlet
2. Turn Robot on, release its brakes, and enable it.
3. Plug USB-C ethernet adaptor into your PC.
4. On the UR3 teach pendant, go to settings, then network.
5. Confirm Robot is connected to the network (this may take a couple of minutes).
6. On your PC, you will have to manually add the DNS.
7. Test the connection by running "Robot.py", and typing "idle" in the terminal.

Commands:
- "home" = Moves the robot to the default upright joint position.
- "idle" = Moves the robot to the idle position, which overlooks the chessboard, camera fits whole board.
- "open" = Opens the NewScale Precision gripper.
- "close" = Close the NewScale Precision gripper.

Move the Robot to an individual square:
- Type in the square. Ex: "a1", "h8".
- Type in "up" or "u" to move above the square, as if the robot is holding a piece.
- Anything else will be read as down, and the robot moves to the z height to drop a piece.




