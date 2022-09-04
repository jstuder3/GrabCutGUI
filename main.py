from tkinter import filedialog
import numpy as np
from scipy.ndimage import zoom
import cv2 as cv
from matplotlib import pyplot as plt

#GUI
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image, ImageGrab


import sys
import os

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

#import other modules
from utils.gui import PaintGUI
import utils.config as config

#startup parameters
config.img_name=""
config.current_filename = ""
config.input_path = ""
config.output_path = ""

config.DEFAULT_QUALITY = 8
config.downsampling_quotient = config.DEFAULT_QUALITY

config.original_width = 0
config.original_height = 0

config.canvas_width = 1500
config.canvas_height = int(round(config.canvas_width/1.5))

config.DEFAULT_PEN_SIZE = 70

if __name__ == '__main__':
    PaintGUI()