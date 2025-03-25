# https://robotiq.zendesk.com/hc/en-us/articles/4403928641427-Retrieving-Robotiq-Wrist-Camera-pictures-on-a-computer
# showing image in tkinter window
import requests 
from io import BytesIO
from PIL import Image

# computer vision
import cv2
import numpy as np

def updateImage():
  try: 
    response = requests.get("http://10.20.59.13:4242/current.jpg?type=color")

    # global im, label
    # im = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
    image = Image.open(BytesIO(response.content))
    image.save("chessboard.jpg", format="JPEG")
    # label.config(image=im)
    computerVision("chessboard.jpg")
  except Exception as e:
    print("error getting image from wrist", e)

def computerVision(image):
  image = cv2.imread(image)  # Load an image
  cv2.imshow("Chessboard", image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  gray = np.float32(gray)
  corners = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)
  image[corners > 0.01 * corners.max()] = [0, 0, 255]  # Mark detected corners in red
  cv2.imshow("Corners", image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)  # Adjust (rows, cols) as needed

  if ret:
    cv2.drawChessboardCorners(image, (7, 7), corners, ret)
    cv2.imshow("Detected Chessboard", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

updateImage()