from tkinter import filedialog
import numpy as np
from scipy.ndimage import zoom
import cv2 as cv
from matplotlib import pyplot as plt
import os


#GUI
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image, ImageGrab

import utils.config as config

#produce downsampled image for faster computation
def resize_image(input_path, current_filename, quotient=4):
    img = Image.open(input_path)
    width, height = img.size

    img = img.resize((int(width/quotient), int(height/quotient)))
    
    new_width, new_height = img.size
    img.save(f"{current_filename}_resized.JPG", quality=95)
    img.close()

    return new_width, new_height

def segment_image():

    new_width, new_height = resize_image(config.input_path, config.img_name, config.downsampling_quotient)
    new_width, new_height = resize_image(config.img_name+"_mask.JPG", config.img_name+"_mask", config.downsampling_quotient)

    img = cv.imread(f"{config.img_name}_resized.JPG")
    mask = np.zeros(img.shape[:2],np.uint8)

    rect = (0, 0, new_width-1, new_height-1)

    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    mask, bgdModel, fgdModel = cv.grabCut(img, mask, rect, bgdModel, fgdModel, 10, cv.GC_INIT_WITH_RECT)

    newmask = cv.imread(f"{config.img_name}_mask_resized.JPG", 0)

    mask[newmask == 0] = 0
    mask[newmask==255] = 1

    mask, bgdModel, fgdModel = cv.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_MASK)

    mask = np.where((mask==2)|(mask==0),0,1).astype("uint8")

    full_img = cv.imread(config.input_path)[:mask.shape[0]*config.downsampling_quotient, :mask.shape[1]*config.downsampling_quotient] #need to cut off excess dimensions because downsampling_quotient may not be divisor of image size
    alpha_mask = mask.astype(np.float32)#make smooth alpha interpolation possible

    full_mask = zoom(alpha_mask, config.downsampling_quotient, order=1).astype(float)
    #clip mask because interpolation can apparently overshoot
    #full_mask /= full_mask.max()
    #full_mask = full_mask.clip(0.0, 1.0)
    full_mask = full_mask.round(0).astype("uint8")

    full_img = ((full_img*full_mask[:,:,np.newaxis])).astype("uint8")

    full_background = 255*(1-full_mask)
    full_background = np.stack((full_background, full_background, full_background), 2).astype("uint8")

    full_img = full_img+full_background

    full_img = np.flip(full_img, 2)

    #plt.imshow(full_img)
    #plt.colorbar()
    #plt.show()

    full_img = Image.fromarray(full_img)
    full_img.save(f"{config.img_name}_segmented.JPG")
    full_img.close()

def overlay_cutout_onto_image():

    original_img = np.array(Image.open(config.input_path))
    segmented_img = np.array(Image.open(f"{config.img_name}_segmented.JPG"))
    img_mask = np.array(Image.open(f"{config.img_name}_mask.JPG"))

    cutout_mask = (img_mask[:, :, 0]==0) & (img_mask[:, :, 1] == 255) & (img_mask[:, :, 2] == 255)

    row_matches, col_matches = np.where(cutout_mask==1)

    try: #prevent error when no cutout region is selected
        topmost_index = np.min(row_matches)
        bottommost_index = np.max(row_matches)
        leftmost_index = np.min(col_matches)
        rightmost_index = np.max(col_matches)

        segmented_img[topmost_index:bottommost_index, leftmost_index:rightmost_index] = original_img[topmost_index:bottommost_index, leftmost_index:rightmost_index]

    except:
        print("No cutout region marked. Proceeding...")

    segmented_img = Image.fromarray(segmented_img)
    segmented_img.save(f"{config.output_path}/{config.current_filename}")
    segmented_img.close()

def cleanup():
    os.remove(f"{config.img_name}_mask.JPG")
    os.remove(f"{config.img_name}_resized.JPG")
    os.remove(f"{config.img_name}_mask_resized.JPG")
    os.remove(f"{config.img_name}_segmented.JPG")