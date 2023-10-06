# GrabCutGUI
Simple GUI to quickly and intuitively produce image cutouts based on the OpenCV implementation of GrabCut. Simply mark parts of the image that should be foreground / background and let GrabCut work its magic.

![GrabCutGUI Demo 2-min-min](https://user-images.githubusercontent.com/87820315/188329261-1fa772c8-93da-488d-96f4-0f2efbdfb2f5.jpeg)


# Requirements (may work with other versions)

    Python 3.10.6
    numpy 1.23.2
    scipy 1.9.1
    opencv-python 1.9.1
    matplotlib 3.5.3
    tkinter
    Pillow

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

# Settings
The quality slider determines how smoothly the edges of the objects will be matched. Since GrabCut is too slow to reasonably work with high-res images, the image gets downsampled during processing and the resulting mask gets upsampled later to produce the final full-res segmentation. "1" means full resolution, "4" means 1/4 resolution, etc. As a referenece, for ~20 MP images I would recommend using a value of 8. I wouldn't go below 4 since processing time starts to get out of hand at that point.
