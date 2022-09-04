# GrabCutGUI
Simple GUI to quickly and intuitively produce image cutouts based on the OpenCV implementation of GrabCut. Simply mark parts of the image that should be foreground / background and let GrabCut work its magic.

![GrabCutGUI Demo 2](https://user-images.githubusercontent.com/87820315/188259901-bc3a17d7-7a3a-4a72-a04d-d8897ec1fe19.png)


# Requirements (may work with other versions)

    Python 3.10.6
    numpy 1.23.2
    scipy 1.9.1
    opencv-python 1.9.1
    matplotlib 3.5.3
    tkinter
    Pillow 9.2

# Usage

Start the program using 

    python main.py
    
And then:

1. Load an image and set an output folder.
2. Mark foreground, background and cutout with their respective colours. The cutout regions is a part of the image that should be kept regardless of the segmentation result.
3. Press the scissors button.
4. ???
5. Profit.

Note that there can be only one cutout, as the outer bounds of all pixels marked with the cutout colour serve as the dimensions of a bounding box.
