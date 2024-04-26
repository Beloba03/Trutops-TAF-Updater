# This module contains all the code related to GUI creation and management
import tkinter as tk
from file_handling import *
import multiprocessing as mp
from time import sleep
from tkinter_module import FileUpdaterGUI

# Thanks to https://stackoverflow.com/questions/71884285/tkinter-root-window-mouse-drag-motion-becomes-slower for this solution to high polling rate mouse support!
# Limits the refresh rate of the window to stop the drag operation from lagging
def on_configure(e):
    if e.widget == root:
        sleep(0.005)

# Checks if the script is being run as the main script        
if __name__ == "__main__":
    # Stop the Multiprocessing from entering into an infinite window spawning loop when running the script through PyInstaller EXE
    # https://superfastpython.com/multiprocessing-freeze-support-in-python/
    mp.freeze_support()
    
    root = tk.Tk() # Create root window
    root.bind("<Configure>", on_configure)
    app = FileUpdaterGUI(root) # Create the GUI application
    root.mainloop() # Call Tkinter loop
