# https://robotiq.zendesk.com/hc/en-us/articles/4403928641427-Retrieving-Robotiq-Wrist-Camera-pictures-on-a-computer
import requests 
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk

root = Tk()
root.title("Live Robot Feed")
root.geometry("800x700")

label = Label()
label.grid(row=1, column=0, columnspan=3)

def updateImage():
  try: 
    response = requests.get("http://192.168.1.2:4242/current.jpg?type=color")
    # response = requests.get("http://10.20.59.13:4242/current.jpg?type=edges")

    global im, label
    im = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
    label.config(image=im)
  except Exception as e:
    print("error getting image from wrist", e)

  root.after(100, updateImage) # updates image every n milliseconds after root.mainloop start


root.after(10, updateImage) # starts loop that updates image

root.mainloop()