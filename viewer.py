# Library
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import threading

# Machine Vision Library
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pylon_camera import pylon_camera

# Button Commands 
def Open():
    if open_button.cget("text") == "Open":
        camera.open_by_serialNumber("21894808")
        open_button.config(text="Close")
    else:
        camera.close()
        open_button.config(text="Open")

def Start():
    if start_button.cget("text") == "Start":
        camera.start()
        start_button.config(text="Stop")
        bufferThread = threading.Thread(target=DisplayWorker)
        bufferThread.start()
    else :
        camera.stop()
        if bufferThread is not None:
            bufferThread.join()
        start_button.config(text="Start")

# Display Thread 
def DisplayWorker():
    while camera.is_grabbing:
        if camera.grab_done.is_set():
            # Monochrome Image
            #image = Image.fromarray(camera.buffer.GetArray())

            # Color Image
            image = Image.fromarray(camera.color_buffer.GetArray())
            
            image = image.resize((canvas.winfo_width(), canvas.winfo_height()), Image.Resampling.LANCZOS)
            displayimage = ImageTk.PhotoImage(image)
            canvas.itemconfig(canvas_image, image=displayimage)
            canvas.image = displayimage
            
            camera.grab_done.clear()
#Main Program
if __name__=="__main__":
    camera = pylon_camera()

    window = tk.Tk()
    window.geometry("1920x1080")
    window.resizable(True,True)
    window.title("Machine Vision Image Viewer")
    window.grid_rowconfigure(0, weight=0)
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)

    open_button = tk.Button(window, text="Open",command=Open)
    start_button = tk.Button(window, text="Start", command=Start)
    open_button.grid(column=0,row=0, sticky="nsew")
    start_button.grid(column=1, row=0, sticky="nsew")

    canvas = tk.Canvas(window)
    canvas.grid(column=0, row=1, columnspan=2, sticky="nsew")
    canvas.config(bg="black")
    canvas_image = canvas.create_image(0,0,image=None, anchor='nw')

    bufferThread = None

    window.mainloop()







