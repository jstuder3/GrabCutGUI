from tkinter import filedialog
import numpy as np
from scipy.ndimage import zoom
import cv2 as cv
from matplotlib import pyplot as plt

#GUI
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image, ImageGrab

from utils.segmentation import resize_image, segment_image, overlay_cutout_onto_image, cleanup
import utils.config as config

class PaintGUI(object):

    def __init__(self):
        self.root = Tk()
        self.root.title('Paint')
        self.root.geometry('1920x1080')
        self.root.maxsize(2560,1660)
        self.root.minsize(1650,1000)

        self.paint_tools = Frame(self.root,width=150,height=600,relief="ridge",borderwidth=2)
        self.paint_tools.place(x=0,y=0)

        button_y_foundation = 120
        button_counter = 0
        button_y_offset = 30

        #self.background = ImageTk.PhotoImage(Image.open(input_path))

        self.input_select_button_logo = None
        self.input_select_label = Label(self.paint_tools, text="Dateiauswahl",borderwidth=0,font=('verdana',10,'bold'))
        self.input_select_label.place(x=5,y=10)
        self.input_select_button = Button(self.paint_tools,padx=6,image=self.input_select_button_logo,borderwidth=2,command=self.input_file_selection)
        self.input_select_button.place(x=120,y=10)

        self.input_select_name = Text(self.paint_tools, height = 1, width = 16, font=('verdana',10)) #Text(self.paint_tools, padx=6, text="Keine Datei gewählt..." borderwidth=0, font=('verdana',10,'bold'))
        self.input_select_name.place(x=5, y=40)
        self.input_select_name.insert(END, "Keine Datei...")

        self.output_select_button_logo = None
        self.output_select_label = Label(self.paint_tools, text="Ausgabeordner",borderwidth=0,font=('verdana',10,'bold'))
        self.output_select_label.place(x=5,y=60)
        self.output_select_button = Button(self.paint_tools,padx=6,image=self.input_select_button_logo,borderwidth=2,command=self.output_folder_selection)
        self.output_select_button.place(x=120,y=60)

        self.output_folder_name = Text(self.paint_tools, height = 1, width = 16, font=('verdana',10)) #Text(self.paint_tools, padx=6, text="Keine Datei gewählt..." borderwidth=0, font=('verdana',10,'bold'))
        self.output_folder_name.place(x=5, y=90)
        self.output_folder_name.insert(END, "Kein Ordner...")

        self.pen_logo = ImageTk.PhotoImage(Image.open('icons/Pen_small.png'))
        self.p = Label(self.paint_tools, text="Stift",borderwidth=0,font=('verdana',10,'bold'))
        self.p.place(x=5,y=button_y_foundation)
        self.pen_button = Button(self.paint_tools,padx=6,image=self.pen_logo,borderwidth=2,command=self.use_pen)
        self.pen_button.place(x=120,y=button_y_foundation)

        button_counter+=1

        self.foreground_logo = ImageTk.PhotoImage(Image.open('icons/ffff00_small.png'))
        self.foreground_label = Label(self.paint_tools,borderwidth=0,text='Vordergrund',font=('verdana',10,'bold'))
        self.foreground_label.place(x=5, y=button_y_foundation + button_counter * button_y_offset)
        self.foreground_button = Button(self.paint_tools,image = self.foreground_logo, borderwidth=2,command=self.set_foreground_colour) 
        self.foreground_button.place(x=120,y=button_y_foundation + button_counter * button_y_offset)

        button_counter+=1

        self.background_logo = ImageTk.PhotoImage(Image.open('icons/ff00ff_small.png'))
        self.background_label = Label(self.paint_tools,borderwidth=0,text='Hintergrund',font=('verdana',10,'bold'))
        self.background_label.place(x=5, y=button_y_foundation + button_counter * button_y_offset)
        self.background_button = Button(self.paint_tools,image = self.background_logo, borderwidth=2,command=self.set_background_colour) 
        self.background_button.place(x=120, y=button_y_foundation + button_counter * button_y_offset)

        button_counter+=1

        self.cutout_logo = ImageTk.PhotoImage(Image.open('icons/00ffff_small.png'))
        self.cutout_label = Label(self.paint_tools,borderwidth=0,text='Cutout',font=('verdana',10,'bold'))
        self.cutout_label.place(x=5, y=button_y_foundation + button_counter * button_y_offset)
        self.cutout_button = Button(self.paint_tools,image = self.cutout_logo, borderwidth=2,command=self.set_cutout_colour) 
        self.cutout_button.place(x=120, y=button_y_foundation + button_counter * button_y_offset)

        button_counter+=1

        self.eraser_logo = ImageTk.PhotoImage(Image.open('icons/Eraser_small.png'))
        self.e = Label(self.paint_tools, text='Radierer',font=('verdana',10,'bold'))
        self.e.place(x=5,y=button_y_foundation + button_counter * button_y_offset)
        self.eraser_button = Button(self.paint_tools,image = self.eraser_logo,borderwidth=2,command=self.use_eraser)
        self.eraser_button.place(x=120,y=button_y_foundation + button_counter * button_y_offset)

        button_counter+=1

        self.scissors_logo = ImageTk.PhotoImage(Image.open('icons/Scissors_small.png'))
        self.scissors_label = Label(self.paint_tools, borderwidth = 0, text="Zuschneiden", font=("veranda", 10, "bold"))
        self.scissors_label.place(x=5, y=button_y_foundation + button_counter * button_y_offset)
        self.scissors_button = Button(self.paint_tools, image=self.scissors_logo, borderwidth = 2, command=self.compute_segmentation)
        self.scissors_button.place(x=120, y=button_y_foundation + button_counter * button_y_offset)

        button_counter+=1

        self.pen_size = Label(self.paint_tools,text="Grösse",font=('verdana',10,'bold'))
        self.pen_size.place(x=5,y=button_y_foundation + button_counter * button_y_offset)
        self.choose_size_button = Scale(self.paint_tools, from_=1, to=200, orient=HORIZONTAL)
        self.choose_size_button.set(config.DEFAULT_PEN_SIZE)
        self.choose_size_button.place(x=15,y=button_y_foundation + button_counter * button_y_offset + 20)

        button_counter+=1

        self.quality_label = Label(self.paint_tools,text="Qualität (1=Best)",font=('verdana',10,'bold'))
        self.quality_label.place(x=5, y=button_y_foundation + button_counter * button_y_offset + 30)
        self.quality_slider = Scale(self.paint_tools, from_=1, to=32, orient=HORIZONTAL)
        self.quality_slider.set(config.DEFAULT_QUALITY)
        self.quality_slider.place(x=15,y=button_y_foundation + button_counter * button_y_offset + 30 + 20)

        button_counter+=1

        #self.c = Canvas(self.root, width=config.canvas_width, height=config.canvas_height,relief=RIDGE, borderwidth=1)
        #self.c.place(x=150,y=0)

        #self.c.create_image(0, 0, anchor=NW, image=self.background)

        # KEYBINDS
        #self.root.bind("1", lambda event:self.use_pen())
        self.root.bind("1", lambda event:self.set_foreground_colour())
        self.root.bind("2", lambda event:self.set_background_colour())
        self.root.bind("3", lambda event:self.set_cutout_colour())
        self.root.bind("4", lambda event:self.use_eraser())
        #self.root.bind("6", lambda event:self.compute_segmentation())
        self.root.bind("<Return>", lambda event:self.compute_segmentation())

        self.setup()
        self.root.mainloop()

    def set_foreground_colour(self):
        self.activate_button(self.pen_button)
        self.pen_button.config(relief=SUNKEN)
        self.foreground_button.config(relief=SUNKEN)
        self.background_button.config(relief=RAISED)
        self.cutout_button.config(relief=RAISED)
        self.color = "#ffff00"
    
    def set_background_colour(self):
        self.activate_button(self.pen_button)
        self.pen_button.config(relief=SUNKEN)
        self.foreground_button.config(relief=RAISED)
        self.background_button.config(relief=SUNKEN)
        self.cutout_button.config(relief=RAISED)
        self.color = "#ff00ff"

    def set_cutout_colour(self):
        self.activate_button(self.pen_button)
        self.pen_button.config(relief=SUNKEN)
        self.foreground_button.config(relief=RAISED)
        self.background_button.config(relief=RAISED)
        self.cutout_button.config(relief=SUNKEN)
        self.color = "#00ffff"

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
        self.pen_button.config(relief=RAISED)
        self.foreground_button.config(relief=RAISED)
        self.background_button.config(relief=RAISED)
        self.cutout_button.config(relief=RAISED)

    def input_file_selection(self):
        filename = filedialog.askopenfilename()

        config.input_path = filename
        config.current_filename = filename.split("/")[-1]
        config.img_name = config.current_filename.split(".")[0]

        #load image size 
        img = Image.open(config.input_path)
        config.original_width, config.original_height = img.size
        img.close()

        #set canvas size based on aspect ratio of image
        aspect_ratio = float(config.original_width) / float(config.original_height)
        config.canvas_height = int(round(config.canvas_width/aspect_ratio))

        self.background = ImageTk.PhotoImage(Image.open(filename).resize((config.canvas_width, config.canvas_height)))

        #create canvas with the selected image as background
        self.c = Canvas(self.root, width=config.canvas_width, height=config.canvas_height, relief=RIDGE, borderwidth=1)
        self.c.place(x=150,y=0)

        self.c.create_image(0, 0, anchor=NW, image=self.background)

        #make key binds
        self.c.bind("<B1-Motion>", self.paint)
        self.c.bind("<ButtonRelease-1>", self.reset)

        self.input_select_name.delete("1.0", END)
        self.input_select_name.insert(END, config.input_path.split("/")[-1])

    def output_folder_selection(self):
        foldername = filedialog.askdirectory()

        config.output_path = foldername

        self.output_folder_name.delete("1.0", END)
        self.output_folder_name.insert(END, config.output_path.split("/")[-1])

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

        #set quality based on slider
        config.downsampling_quotient = self.quality_slider.get()

        #produce mask based on colour markings
        self.produce_and_save_mask()

        #produce segmented image
        segment_image()

        # cut out the part that is marked with the cutout-colour, then put it onto finished image as a post-processing step
        overlay_cutout_onto_image()
        
        cleanup()

    def produce_and_save_mask(self):
        widget = self.c
        x=self.root.winfo_rootx()+widget.winfo_x()
        y=self.root.winfo_rooty()+widget.winfo_y()
        x1=x+widget.winfo_width()
        y1=y+widget.winfo_height()

        img = ImageGrab.grab().crop((x,y,x1,y1))
        img = img.resize((config.original_width, config.original_height))

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
        img.save(f"{config.img_name}_mask.JPG")
        img.close()

    def reset(self, event):
        self.old_x, self.old_y = None, None

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = "#ffff00"
        self.eraser_on = False
        self.active_button = self.pen_button
        self.pen_button.config(relief=SUNKEN)
        self.foreground_button.config(relief=SUNKEN)
        #self.c.bind("<B1-Motion>", self.paint)
        #self.c.bind("<ButtonRelease-1>", self.reset)