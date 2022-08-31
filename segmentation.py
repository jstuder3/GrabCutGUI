import numpy as np
from scipy.ndimage import zoom
import cv2 as cv
from PIL import Image
from matplotlib import pyplot as plt

#GUI
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image, ImageGrab


img_number="770"
downsampling_quotient = 8

img = Image.open(f"data/images/{img_number}.JPG")
original_width, original_height = img.size
img.close()

canvas_width = 1500
canvas_height = int(round(canvas_width/1.5))


class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()
        self.root.title('Paint')
        self.root.geometry('1920x1080')
        self.root.maxsize(1920,1080)
        self.root.minsize(1650,1000)

        self.paint_tools = Frame(self.root,width=150,height=300,relief="ridge",borderwidth=2)
        self.paint_tools.place(x=0,y=0)

        img = Image.open(f"data/images/{img_number}.JPG")
        image_width, image_height = img.size
        #new_image_width = int(image_width / canvas_quotient)
        #new_image_height = int(image_height / canvas_quotient)

        img = img.resize((canvas_width, canvas_height))
        img.save(f"data/images/{img_number}.png")
        img.close()

        self.background = PhotoImage(file = f"data/images/{img_number}.png")

        self.pen_logo = ImageTk.PhotoImage(Image.open('icons/Pen_small.png'))
        self.p = Label(self.paint_tools, text="Stift",borderwidth=0,font=('verdana',10,'bold'))
        self.p.place(x=5,y=10)
        self.pen_button = Button(self.paint_tools,padx=6,image=self.pen_logo,borderwidth=2,command=self.use_pen)
        self.pen_button.place(x=120,y=10)

        self.foreground_logo = ImageTk.PhotoImage(Image.open('icons/ffff00_small.png'))
        self.foreground_label = Label(self.paint_tools,borderwidth=0,text='Vordergrund',font=('verdana',10,'bold'))
        self.foreground_label.place(x=5, y=40)
        self.foreground_button = Button(self.paint_tools,image = self.foreground_logo, borderwidth=2,command=self.set_foreground_colour) 
        self.foreground_button.place(x=120,y=40)

        self.background_logo = ImageTk.PhotoImage(Image.open('icons/ff00ff_small.png'))
        self.background_label = Label(self.paint_tools,borderwidth=0,text='Hintergrund',font=('verdana',10,'bold'))
        self.background_label.place(x=5, y=70)
        self.background_button = Button(self.paint_tools,image = self.background_logo, borderwidth=2,command=self.set_background_colour) 
        self.background_button.place(x=120, y=70)

        self.cutout_logo = ImageTk.PhotoImage(Image.open('icons/00ffff_small.png'))
        self.cutout_label = Label(self.paint_tools,borderwidth=0,text='Cutout',font=('verdana',10,'bold'))
        self.cutout_label.place(x=5, y=100)
        self.cutout_button = Button(self.paint_tools,image = self.cutout_logo, borderwidth=2,command=self.set_cutout_colour) 
        self.cutout_button.place(x=120, y=100)

        self.eraser_logo = ImageTk.PhotoImage(Image.open('icons/Eraser_small.png'))
        self.e = Label(self.paint_tools, text='Radierer',font=('verdana',10,'bold'))
        self.e.place(x=5,y=130)
        self.eraser_button = Button(self.paint_tools,image = self.eraser_logo,borderwidth=2,command=self.use_eraser)
        self.eraser_button.place(x=120,y=130)

        self.scissors_logo = ImageTk.PhotoImage(Image.open('icons/Scissors_small.png'))
        self.scissors_label = Label(self.paint_tools, borderwidth = 0, text="Zuschneiden", font=("veranda", 10, "bold"))
        self.scissors_label.place(x=5, y=160)
        self.scissors_button = Button(self.paint_tools, image=self.scissors_logo, borderwidth = 2, command=self.compute_segmentation)
        self.scissors_button.place(x=120, y=160)

        self.pen_size = Label(self.paint_tools,text="Grösse",font=('verdana',10,'bold'))
        self.pen_size.place(x=5,y=190)
        self.choose_size_button = Scale(self.paint_tools, from_=1, to=40, orient=HORIZONTAL)
        self.choose_size_button.set(20)
        self.choose_size_button.place(x=15,y=210)

        self.c = Canvas(self.root, width=canvas_width, height=canvas_height,relief=RIDGE, borderwidth=1)
        self.c.place(x=150,y=0)

        self.c.create_image(0, 0, anchor=NW, image=self.background)

        self.setup()
        self.root.mainloop()

    def set_foreground_colour(self):
        self.color = "#ffff00"
    
    def set_background_colour(self):
        self.color = "#ff00ff"

    def set_cutout_colour(self):
        self.color = "#00ffff"

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def compute_segmentation(self):
        #produce mask based on colour markings
        self.produce_and_save_mask()

        #produce segmented image
        segment_image()

        # cut out the part that is marked with the cutout-colour, then put it onto finished image as a post-processing step
        overlay_cutout_onto_image()

    def produce_and_save_mask(self):
        widget = self.c
        x=self.root.winfo_rootx()+widget.winfo_x()
        y=self.root.winfo_rooty()+widget.winfo_y()
        x1=x+widget.winfo_width()
        y1=y+widget.winfo_height()
        #ImageGrab.grab().crop((x,y,x1,y1)).save(f"data/masks/{img_number}_mask.jpg")

        img = ImageGrab.grab().crop((x,y,x1,y1))#.save(f"data/masks/{img_number}_mask.jpg")
        img = img.resize((original_width, original_height))

        #post-processing of mask: replace colour values to produce "cleaned" mask
        img = np.array(img)

        #replace every pixel that does not have a special colour with gray (this is apparently not quite straightforward)
        mask = ((img[:, :, 0]==255) & (img[:, :, 1]==255) & (img[:, :, 2]==0)) | ((img[:, :, 0]==255) & (img[:, :, 1]==0) & (img[:, :, 2]==255)) | ((img[:, :, 0]==0) & (img[:, :, 1]==255) & (img[:, :, 2]==255))
        img[:, :, :3][mask==0]=[128, 128, 128]

        #turn every yellow pixel white (foreground)
        foreground_mask = (img[:, :, 0]==255) & (img[:, :, 1]==255) & (img[:, :, 2]==0)
        img[:, :, :3][foreground_mask] = [255, 255, 255]

        #turn every purple pixel black (background)
        background_mask = (img[:, :, 0]==255) & (img[:, :, 1]==0) & (img[:, :, 2]==255)
        img[:, :, :3][background_mask] = [0, 0, 0]

        #keep the cutout pixels the same, then save

        img = Image.fromarray(img)
        img.save(f"data/masks/{img_number}_mask.jpg")
        img.close()


    #def save_as_jpg(self):
    #    self.c.postscript(file=f"data/eps/{img_number}.eps")
    #    img = Image.open(f"data/eps/{img_number}.eps")
    #    img = img.resize((original_width, original_height), resample=Image.Resampling.NEAREST)
    #    img.save(f"data/masks/{img_number}.jpg", quality=95)

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = "#ffff00" #self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button #self.foreground_button #self.brush_button
        self.c.bind("<B1-Motion>", self.paint)
        self.c.bind("<ButtonRelease-1>", self.reset)
    

#produce downsampled image for faster computation
def resize_image(img_path, quotient=4):
    img = Image.open(f"data/{img_path}.JPG")
    width, height = img.size

    img = img.resize((int(width/quotient), int(height/quotient)))
    
    new_width, new_height = img.size
    img.save(f"data/resized/{img_path}_resized.JPG", quality=95)
    img.close()

    return new_width, new_height

def segment_image():

    new_width, new_height = resize_image("images/"+img_number, downsampling_quotient)
    new_width, new_height = resize_image("masks/"+img_number+"_mask", downsampling_quotient)

    img = cv.imread(f"data/resized/images/{img_number}_resized.JPG")
    mask = np.zeros(img.shape[:2],np.uint8)

    rect = (0, 0, new_width-1, new_height-1)

    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)

    mask, bgdModel, fgdModel = cv.grabCut(img, mask, rect, bgdModel, fgdModel, 10, cv.GC_INIT_WITH_RECT)

    newmask = cv.imread(f"data/resized/masks/{img_number}_mask_resized.JPG", 0)

    mask[newmask == 0] = 0
    mask[newmask==255] = 1

    mask, bgdModel, fgdModel = cv.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_MASK)

    mask = np.where((mask==2)|(mask==0),0,1).astype("uint8")

    full_img = cv.imread(f"data/images/{img_number}.JPG")[:mask.shape[0]*downsampling_quotient, :mask.shape[1]*downsampling_quotient] #need to cut off excess dimensions because downsampling_quotient may not be divisor of image size
    alpha_mask = mask.astype(np.float32)#make smooth alpha interpolation possible

    full_mask = zoom(alpha_mask, downsampling_quotient, order=1).astype(float)
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
    full_img.save(f"data/segmented_images/{img_number}.JPG")
    full_img.close()

def overlay_cutout_onto_image():
    original_img = np.array(Image.open(f"data/images/{img_number}.JPG"))
    segmented_img = np.array(Image.open(f"data/segmented_images/{img_number}.JPG"))
    img_mask = np.array(Image.open(f"data/masks/{img_number}_mask.JPG"))

    cutout_mask = (img_mask[:, :, 0]==0) & (img_mask[:, :, 1] == 255) & (img_mask[:, :, 2] == 255)

    row_matches, col_matches = np.where(cutout_mask==1)

    topmost_index = np.min(row_matches)
    bottommost_index = np.max(row_matches)
    leftmost_index = np.min(col_matches)
    rightmost_index = np.max(col_matches)

    segmented_img[topmost_index:bottommost_index, leftmost_index:rightmost_index] = original_img[topmost_index:bottommost_index, leftmost_index:rightmost_index]

    segmented_img = Image.fromarray(segmented_img)
    segmented_img.save(f"data/post_processed_images/{img_number}.JPG")
    segmented_img.close()

if __name__ == '__main__':
    Paint()