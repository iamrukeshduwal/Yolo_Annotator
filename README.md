# YOLO Annotator - Image Annotation Tool

Author: Rukesh Duwal
Date: January 30th, 2024
Occupation: Computer Vision Engineer at Crimson Tech
License: MIT License

## Description

The YOLO Annotator is a simple image annotation tool developed in Python using Tkinter for graphical user interface elements.

## Key Features

- Annotation of bounding boxes.
- Keyboard shortcuts for quick navigation.

## Main Program and Credits

- Main Program forked from [puzzledqs/BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool/tree/multi-class)
- Converter to YOLO format forked from [ManivannanMurugavel/YOLO-Annotation-Tool](https://github.com/ManivannanMurugavel/YOLO-Annotation-Tool)

## Usage

1. For multi-class tasks, modify 'class.txt' with your class candidates. Before labeling a bounding box, choose the 'Current Class' in the Combobox or by pressing <kbd>1-9</kbd> on your keyboard.
2. Run `python main.py`.
3. Click `LoadImage`, select a folder that contains a list of images.
4. To create a new bounding box, left-click to select the first vertex. Move the mouse to draw a rectangle and left-click again to select the second vertex.
   - To delete the bounding box while drawing, <kbd>right click</kbd>.
   - To delete an existing bounding box,click inside box or  select it from the listbox and click `Clear`.
   - To delete all existing bounding boxes in the image, click `ClearAll` or press <kbd>r</kbd>.
5. After finishing one image, click `Next` or press <kbd>d</kbd> to advance. Click `Prev` or press <kbd>a</kbd> to reverse. Alternatively, input the index and click `Go` to navigate to an arbitrary image.
   - The labeling result will be saved in **Labels/[folder name]/..** only if the 'Next' button is clicked.
   - **The checkpoint of the last Image Number will be saved when the 'Next' button is clicked.**
6. Click `Skip` to skip an unwanted image from the directory and skip the annotation for that image (the skipped image path will be saved in log/skip.txt).
7. Click `ConvertYOLO` or press <kbd>c</kbd> to convert the labeling result to YOLO format. The result will be saved in **Result_YOLO/[folder name]/..**

## How to Run

1. Make sure you have Python installed on your system.
2. Clone this repository:
   git clone https://github.com/iamrukeshduwal/Yolo_Annotator.git
   cd Yolo_Annotator
   python main.py

## License
Feel free to copy and paste this content into your README.md file. If you have more changes or specific details to add, please let me know!


