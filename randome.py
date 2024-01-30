from tkinter import *
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter

import os
import glob
import convert

# colors for the bboxes
COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black', 'purple', 'orange', 'brown']

# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("Yolo Annotator")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=True)
        self.parent.resizable(width=FALSE, height=FALSE)

        # color picker
        self.index = 0

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.xmlOutDir = ''
        self.cur = 0
        self.total = 0
        self.category = ''
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.classcandidate_filename = 'class.txt'
        self.classcnt = 0

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None
        self.selected_bbox = None

        self.class_to_color = {}

        # ----------------- GUI stuff ---------------------

        self.ldProjBtn = Button(self.frame, text="Load Image", command=self.loadDir)
        self.ldProjBtn.grid(row=0, column=0, sticky=W + E, padx=5)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Button-3>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("a", self.prevImage)  # press 'a' to go backforward
        self.parent.bind("d", self.nextImage)  # press 'd' to go forward
        self.parent.bind("r", self.clearBBoxShortcut)
        self.mainPanel.grid(row=1, column=1, columnspan=3, rowspan=4, sticky=W + N)

        # Add scrollbars
        # Choose class display
        self.lb1_ = Label(self.frame, text='Choose Class')
        self.lb1_.grid(row=2, column=4, sticky=W + N)

        # choose class
        self.classname = StringVar()
        self.classcandidate = ttk.Combobox(self.frame, state='readonly', textvariable=self.classname)
        self.classcandidate.grid(row=1, column=4)
        if os.path.exists(self.classcandidate_filename):
            with open(self.classcandidate_filename) as cf:
                for line in cf.readlines():
                    # print line
                    self.cla_can_temp.append(line.strip('\n'))
                    self.classcnt += 1

        self.classcandidate['values'] = self.cla_can_temp
        self.classcandidate.current(0)
        self.parent.bind('<Key>', self.setClassShortcut)

        self.currentLabelclass = self.classcandidate.get()  # init
        self.classcandidate.bind('<<ComboboxSelected>>', self.setClass)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=3, column=4, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=12)
        self.listbox.grid(row=4, column=4, sticky=N + S)
        self.btnDel = Button(self.frame, text='Clear', command=self.delBBox)
        self.btnDel.grid(row=5, column=4, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=6, column=4, sticky=W + E + N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=7, column=1, columnspan=4, sticky=W + E)
        self.conv2YoloBtn = Button(self.ctrPanel, text='Convert YOLO', width=15, command=self.convert2Yolo)
        self.conv2YoloBtn.pack(side=LEFT, padx=5, pady=3)
        self.resetChkBtn = Button(self.ctrPanel, text='ResetCheckpoint', width=15, command=self.resetCheckpoint)
        self.resetChkBtn.pack(side=LEFT, padx=5, pady=3)
        self.loadChkBtn = Button(self.ctrPanel, text='LoadCheckpoint', width=15, command=self.loadCheckpoint)
        self.loadChkBtn.pack(side=LEFT, padx=5, pady=3)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.skipBtn = Button(self.ctrPanel, text='Skip', width=10, command=self.skipImage)
        self.skipBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border=10)
        self.egPanel.grid(row=1, column=0, rowspan=5, sticky=N)
        self.tmpLabel2 = Label(self.egPanel,
                               text="Key Shortcut :\na : Prev\nd : Next\nr : Delete BB\n1-9 : Select Class")
        self.tmpLabel2.pack(side=TOP)
        self.tmpLabel3 = Label(self.egPanel, text="\nBasic Usage :\n1.Load Image\n2.Annotate\n3.Convert Yolo")
        self.tmpLabel3.pack(side=TOP)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side=TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def get_class_index(self, class_name):
        try:
            class_index = self.cla_can_temp.index(class_name)
            return class_index
        except ValueError:
            print(f"Class '{class_name}' not found in the list.")
            return None

    # -----------------------Function For Load Directory--------------------------------
    def loadDir(self, dbg=False):
        self.imageList = []
        if not dbg:
            self.parent.focus()
            s = str(filedialog.askdirectory(initialdir=os.getcwd())).split('/')[-1]
            self.category = s
        else:
            s = r'D:\workspace\python\labelGUI'
        self.imageDir = os.path.join(r'./Images', '%s' % (self.category))
        for ext in ('*.png', '*.jpg'):
            self.imageList.extend(glob.glob(os.path.join(self.imageDir, ext)))
        if len(self.imageList) == 0:
            messagebox.showinfo("Error", "No JPG/PNG images found in the specified dir!")
            print('No JPG/PNG images found in the specified dir!')
            return
        self.cur = 1
        self.total = len(self.imageList)
        self.outDir = os.path.join(r'./Result', '%s' % (self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        self.loadImage()  # Call Function to load the image
        print('%d images loaded from %s' % (self.total, self.category))
        messagebox.showinfo("Info", "%d images loaded from %s" % (self.total, self.category))

    # ----------------------------------------------------------------------------------------

    # --------------------Function to load Image From Directory--------------------------------
    def loadImage(self):
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)

        # Clear the existing mainPanel and reconfigure
        self.mainPanel.destroy()

        frame = Frame(self.frame)
        frame.grid(row=1, column=1, columnspan=3, rowspan=4, sticky=W + N)

        hbar = Scrollbar(frame, orient=HORIZONTAL)
        vbar = Scrollbar(frame, orient=VERTICAL)

        self.mainPanel = Canvas(frame, cursor='tcross', width=1200, height=630, scrollregion=(0, 0, self.tkimg.width(), self.tkimg.height()), xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.pack(side=BOTTOM, fill=X)
        vbar.pack(side=RIGHT, fill=Y)
        self.mainPanel.pack(side=LEFT, expand=YES, fill=BOTH)

        hbar.config(command=self.mainPanel.xview)
        vbar.config(command=self.mainPanel.yview)

        self.mainPanel.bind("<MouseWheel>", self.scrollCanvas)
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)

        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))
        self.clearBBox()

        self.imagename = os.path.split(imagepath)[-1]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)

        self.loadBBox()


    def configureCanvas(self, event):
        self.mainPanel.config(scrollregion=self.mainPanel.bbox("all"))

    def scrollCanvas(self, event):
        if event.delta:
            self.mainPanel.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 5:
                move = 1
            else:
                move = -1
            self.mainPanel.yview_scroll(move, "units")

    # ---------------------------------------------------------------------------------------------

    # ----------------------------------Function to saveImage--------------------------------
    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' % len(self.bboxList))
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved' % (self.cur))
    # ------------------------------------------------------------------------------------------

    # --------------------------------------Function to return x,y cooriantes while mouse click on mainPanel canvas--------------------------------
    def mouseClick(self, event):
        if self.tkimg:
            if event.num == 1:  # Left mouse button clicked
                if self.STATE['click'] == 0:
                    self.STATE['x'], self.STATE['y'] = event.x, event.y
                else:
                    x1, y1 = self.mainPanel.canvasx(self.STATE['x']), self.mainPanel.canvasy(self.STATE['y'])
                    x2, y2 = self.mainPanel.canvasx(event.x), self.mainPanel.canvasy(event.y)
                    self.bboxList.append((x1, y1, x2, y2, self.currentLabelclass))
                    self.bboxIdList.append(self.bboxId)
                    self.bboxId = None
                    self.listbox.insert(END, '%s : (%d, %d) -> (%d, %d)' % (
                        self.currentLabelclass, x1, y1, x2, y2))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[self.index])
                self.STATE['click'] = 1 - self.STATE['click']
            elif event.num == 3:  # Right mouse button clicked
                self.removeBBox(event)

    # --------------------------Function to return x,y coordinates while moving mouse over mainPanel canvas--------------------
    def mouseMove(self, event):
        if self.tkimg:
            self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
            if self.tkimg:
                if self.hl:
                    self.mainPanel.delete(self.hl)
                self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
                if self.vl:
                    self.mainPanel.delete(self.vl)
                self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
            if 1 == self.STATE['click']:
                if self.bboxId:
                    self.mainPanel.delete(self.bboxId)
                x1, y1 = self.mainPanel.canvasx(self.STATE['x']), self.mainPanel.canvasy(self.STATE['y'])
                x2, y2 = self.mainPanel.canvasx(event.x), self.mainPanel.canvasy(event.y)
                self.bboxId = self.mainPanel.create_rectangle(x1, y1, x2, y2, width=2, outline=COLORS[self.index])



    def convert2Yolo(self):
        self.checkImage()
        yolo_data = convert.convert_format(self.labelfilename, self.tkimg.width(), self.tkimg.height())
        with open(self.labelfilename, 'w') as f:
            f.write(yolo_data)
        print('Label file for YOLO format converted.')

    def resetCheckpoint(self):
        if os.path.exists(self.labelfilename):
            os.remove(self.labelfilename)
            print('Reset the annotation for %s' % self.imagename)
        else:
            print('No annotation file found for %s' % self.imagename)

    def loadCheckpoint(self):
        if os.path.exists(self.labelfilename):
            self.loadBBox()
            print('Previous annotation for %s loaded.' % self.imagename)
        else:
            print('No annotation file found for %s' % self.imagename)

    def setClass(self, event=None):
        self.currentLabelclass = self.classcandidate.get()
        print('set label class to :', self.currentLabelclass)

    def setClassShortcut(self, event):
        if event.char.isdigit() and 1 <= int(event.char) <= len(self.cla_can_temp):
            index = int(event.char) - 1
            self.currentLabelclass = self.cla_can_temp[index]
            self.classcandidate.set(self.currentLabelclass)
            print('set label class to :', self.currentLabelclass)

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def clearBBoxShortcut(self, event):
        self.clearBBox()

    def loadBBox(self):
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = line.split()
                    self.bboxList.append(tuple(tmp))
                    idx = self.bboxList[i - 1][-1]
                    idx_1 = self.get_class_index(idx)
                    x1, y1 = self.mainPanel.canvasx(int(tmp[0])), self.mainPanel.canvasy(int(tmp[1]))
                    x2, y2 = self.mainPanel.canvasx(int(tmp[2])), self.mainPanel.canvasy(int(tmp[3]))
                    tmpId = self.mainPanel.create_rectangle(x1, y1, x2, y2, width=2, outline=COLORS[idx_1])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%s : (%d, %d) -> (%d, %d)' % (tmp[4], x1, y1, x2, y2))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[idx_1])


    def prevImage(self, event=None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def skipImage(self):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        self.saveImage()
        idx = int(self.idxEntry.get())
        if 1 <= idx <= self.total:
            self.cur = idx
            self.loadImage()

    def checkImage(self):
        if self.tkimg:
            self.saveImage()

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)

    root.mainloop()
