import cv2
import os
import sys
import easygui
import numpy as np
import json
import pickle
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import math
import shutil
import PIL
from PIL import Image, ImageTk
from scipy.spatial.distance import euclidean
import natsort
from AppKit import NSScreen
import keyboard

from summarize import summarize

import sqlite3


cntrlPts = ["1104", "1105", "1106", "1107", "1111", "1112", "1113", "1114", "1115", "1116", "1120", "1121", "1122", "1123",
"1124", "1127", "1128", "1129", "1130", "1131", "1132", "1135", "1136", "1137", "1138", "1139", "1140", "1141", "1145", "1146",
"1148", "2002", "2004", "2005", "2006", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2017", "2018", "2019", "2020",
"2021", "2024", "2025", "2026", "2027", "2028", "2029", "2030", "2033", "2034", "2035", "2036"]

class CheckboxListbox(tk.Frame):
    def __init__(self, parent, items, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.vars = []
        self.checkbtn = []
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas to hold the checkboxes
        canvas = tk.Canvas(self, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Attach scrollbar to canvas
        scrollbar.config(command=canvas.yview)

        # Create a frame inside the canvas for checkboxes
        checkbox_frame = tk.Frame(canvas)
        checkbox_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Add the frame to the canvas
        self.checkbox_window = canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

        self.style = ttk.Style()

        # Add checkboxes for the items
        for item in items:
            var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(checkbox_frame, text=item, variable=var)
            checkbox.pack(anchor=tk.W)
            self.vars.append(var)
            self.checkbtn.append(checkbox)

    def get_checked_items(self):
        return [var.get() for var in self.vars]
    
    def selectItems(self,val):
        self.vars[cntrlPts.index(val)].set(True)
        self.style.configure( self.checkbtn[cntrlPts.index(val)], foreground='green')

    def clearAllItems(self):
        for var in self.vars:
            var.set(False)

class UI:
    
    def __init__(self):
        self.rootUI = tk.Tk()
        self.rootUI.grid_columnconfigure(0,weight=0)
        self.rootUI.grid_rowconfigure(0,weight=1)
        self.rootUI.grid_columnconfigure(1,weight=1)
        self.rootUI.grid_columnconfigure(2,weight=0)
        self.rootUI.grid_columnconfigure(3,weight=0)

        # get usable screen resolution
        screen = NSScreen.mainScreen()
        visible_frame = screen.visibleFrame()
        usable_width = visible_frame.size.width
        usable_height = visible_frame.size.height
        offset_x = visible_frame.origin.x
        offset_y = visible_frame.origin.y

        self.rootUI.geometry(f"{int(usable_width)}x{int(usable_height)}")

        self.filez = []
        
        self.frame1 = tk.Frame(self.rootUI)
        self.frame2 = tk.Frame(self.rootUI)
        self.frame3 = tk.Frame(self.rootUI)
        self.frame4 = tk.Frame(self.rootUI)
        
        self.frame1.grid(row=0,column=0,sticky="ns")
        self.frame2.grid(row=0, column=1,sticky="nsew")
        self.frame3.grid(row=0, column=2,sticky="nsew")
        self.frame4.grid(row=0, column=3,sticky="nsew")
        
        # coloumn 1 (left hand side of the UI) 
        self.frame1_1 = tk.Frame(self.frame1)
        self.frame1_2 = tk.Frame(self.frame1)
        self.frame1_3 = tk.Frame(self.frame1)
        
        self.list_of_files_widget = tk.Listbox(self.frame1_2,selectmode="single")
                
        self.scroll_list_of_files= tk.Scrollbar(self.frame1_2,orient="vertical")
        self.scroll_list_of_files.config(command=self.list_of_files_widget.yview)
        
        self.list_of_files_widget.config(yscrollcommand=self.scroll_list_of_files.set)
        
        self.list_of_files_widget.pack(side="left", fill="y")
        self.scroll_list_of_files.pack(side='right',fill="y")
        
        self.list_of_files_widget.bind("<<ListboxSelect>>",self.updateCurrentSelection)
        
        self.pathBtn = tk.Button(self.frame1_1, text="Select Path", command=self.pickDirectory)
        self.refreshBtn = tk.Button(self.frame1_3, text="Refresh")
        
        self.pathBtn.pack()
        self.refreshBtn.pack()
        
        self.frame1.grid_columnconfigure(0,weight=1)
        self.frame1.grid_rowconfigure(0,weight=0)
        self.frame1.grid_rowconfigure(1,weight=1)
        self.frame1.grid_rowconfigure(2,weight=0)
        
        self.frame1_1.grid(row=0,column=0)
        self.frame1_2.grid(row=1,column=0,sticky="ns")
        self.frame1_3.grid(row=3,column=0)
        
        self.itemsStrVar = tk.StringVar()
        self.itemsCounterLabel = tk.Label(self.frame1_3, textvariable=self.itemsStrVar)
        self.itemsStrVar.set("No items found")
        self.itemsCounterLabel.pack()
        
        # coloumn 2 
        self.frame2_1=tk.Frame(self.frame2)
        self.frame2_2=tk.Frame(self.frame2)

        #self.imgcanvas = tk.Canvas(self.frame2_1,height=1536,width=2048,name="image_canvas")
        self.imgcanvas = tk.Canvas(self.frame2_1, name="image_canvas", confine=True)

        self.scroll_image_vertical = tk.Scrollbar(self.frame2_1,orient="vertical")
        self.scroll_image_horizontal = tk.Scrollbar(self.frame2_1,orient="horizontal")
        self.scroll_image_vertical.config(command=self.imgcanvas.yview)
        self.scroll_image_horizontal.config(command=self.imgcanvas.xview)
        self.imgcanvas.config(yscrollcommand=self.scroll_image_vertical.set, xscrollcommand=self.scroll_image_horizontal.set)

        self.scroll_image_vertical.pack(side="right",fill='y')
        self.imgcanvas.pack(fill='both',expand=True)
        self.scroll_image_horizontal.pack(side='bottom',fill='x')

        self.imgcanvas.bind("<MouseWheel>",self.scrollUsingMouse)

        self.idTextVar = tk.StringVar()
        self.idText = tk.Entry(self.frame2_2, textvariable=self.idTextVar)
        self.idTextVar.set("Enter Target Id")
        self.idText.pack(side='left')
        self.idText.bind('<1>',self.clearEntryText)
        self.idText.bind('<Return>',self.mouseClick)
        
        self.okBtn = tk.Button(self.frame2_2,text="Ok", command=self.recordTheTargetID)
        self.okBtn.pack(side='left')
        
        self.nextBtn = tk.Button(self.frame2_2,text="Next",command=self.nextBtnCallback)
        self.nextBtn.pack(side='right')
        
        self.frame2.grid_columnconfigure(0,weight=1)
        self.frame2.grid_rowconfigure(0,weight=1)
        self.frame2.grid_rowconfigure(1,weight=0)
        self.frame2_1.grid(row=0,column=0,sticky="nsew")
        self.frame2_2.grid(row=1, column=0, sticky="ew")
        
        # coloumn 3
        self.frame3_1 = tk.Frame(self.frame3)
        self.list_of_keypoints = tk.Listbox(self.frame3_1,selectmode="single")
                
        self.scroll_list_of_keypoints = tk.Scrollbar(self.frame3_1,orient="vertical")
        self.scroll_list_of_keypoints.config(command=self.list_of_keypoints.yview)
        
        self.list_of_keypoints.config(yscrollcommand=self.scroll_list_of_keypoints.set)
        
        self.list_of_keypoints.pack(side="left", fill="y")
        self.scroll_list_of_keypoints.pack(side='right',fill="y")

        self.frame3.grid_columnconfigure(0,weight=0)
        self.frame3.grid_rowconfigure(0,weight=1)

        self.frame3_1.grid(row=0,column=0,sticky="ns")


        # coloumn 4
        self.cntlptlistbox = CheckboxListbox(self.frame4, cntrlPts)
        self.cntlptlistbox.pack(fill=tk.BOTH, expand=True)
        

        
        # Initialization for writing data into files
        self.master_dict = {}
        self.count = 0
        self.images =[]
        self.ids = []
        self.xp = []
        self.yp = []
        self.tempimgname = '/tmp/highlightedtarget.png'

        self.rootUI.bind("<Button 1>", self.mouseClick)
        self.rootUI.bind('<Return>', self.enterpressed)

        self.rootUI.bind('<Double-Button-1>', self.doubleclickbinder)
        self.rootUI.mainloop()
        
    def updateCurrentSelection(self,event):
        self.list_of_keypoints.delete(0,"end")
        self.cntlptlistbox.clearAllItems()
        self.updateImageCanvas()
        self.populateKeypointslistbox()
        
    def pickDirectory(self):
        self.path_dir = filedialog.askdirectory()
        listoffiles = os.listdir(self.path_dir)
        self.filez = natsort.natsorted(listoffiles)

        #connect to a database 
        #self.sqldb = sqlite3.connect(os.path.join(self.path_dir,".img_key_pts.db"))
        #self.sqldb_cursor = self.sqldb.cursor()

        #try:
        #    self.sqldb_cursor.execute("SELECT * FROM img_keypoints")
        #except:
        #    self.sqldb_cursor.execute('''CREATE TABLE img_keypoints(
        #                             keypoint_id TEXT,
        #                              image TEXT,
        #                              row REAL,
        #                              col REAL,
        #                              radius INTEGER)''')

        self.populateListBox()


    def populateListBox(self):
        for name in self.filez:
            if name.endswith("png") or name.endswith("jpg"):
                if not name.startswith("."):
                    self.list_of_files_widget.insert('end',name)

        self.list_of_files_widget.select_set(0)
        self.itemsStrVar.set(f'Found {self.list_of_files_widget.index("end")} items in directory')
        self.updateImageCanvas()
        self.populateKeypointslistbox()

    def populateKeypointslistbox(self):
        jsonfilename = os.path.join(self.path_dir,self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]+'.json')
        keypointsfilename = os.path.join(self.path_dir,f".{self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]}_keypoints.txt")

        if os.path.exists(jsonfilename):
            with open(jsonfilename, 'r') as file:
                self.master_dict = json.load(file)
        self.count = len(self.master_dict)
        
        if os.path.exists(keypointsfilename):
            # read the keypoints and plot it 
            with open(keypointsfilename,"r") as keypointsread:
                for line in keypointsread:
                    data = line.split('\n')[0].split('\t')
                    self.list_of_keypoints.insert("end", data[0])

                    if data[0] in cntrlPts:
                        self.cntlptlistbox.selectItems(data[0])




                    #self.addToDatabase(data)

    def addToDatabase(self, keypoint):
        command  = f"INSERT INTO img_keypoints(keypoint_id, image, row, col, radius) \
                    SELECT * FROM (SELECT {keypoint[0]}, {keypoint[1]}, {keypoint[3]}, {keypoint[2]}, {1}) as temp\
                    WHERE NOT EXISTS\
                    (SELECT keypoint_id,image  FROM table-name WHERE keypoint_id = {keypoint[0]} and  image = {keypoint[1]} ) LIMIT 1"
        self.sqldb_cursor.execute(command)


    

    def refreshListBox(self):
        self.list_of_files_widget.delete(0,"end")
        self.populateListBox()
        
    def updateImageCanvas(self, filename=None):
        if filename ==None:
            imgfileName = os.path.join(self.path_dir,self.list_of_files_widget.get(self.list_of_files_widget.curselection()))
            backupimagefilename = os.path.join(self.path_dir,f".{self.list_of_files_widget.get(self.list_of_files_widget.curselection())}.backup")
            if not os.path.exists(backupimagefilename):
                shutil.copy2(imgfileName,backupimagefilename)
        else:
            imgfileName = filename

        self.img = Image.open(imgfileName)
        #self.img = self.img.resize((math.ceil(self.img.size[0]/2), math.ceil(self.img.size[1]/2)),Image.Resampling.BICUBIC)
        self.imgTk = ImageTk.PhotoImage(self.img)
        self.imgcanvas.create_image(10,10,anchor='nw',image=self.imgTk)

        # set scrollable area
        self.imgcanvas.configure(scrollregion=(0,0,self.img.width,self.img.height))
        
        # detect blobs from the image
        self.detectTargetsFromImages()
        
    def nextBtnCallback(self):

        # write the master dict to file 
        jsonfilename = os.path.join(self.path_dir,self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]+'.json')
        with open(jsonfilename,'w') as fp:
            json.dump(self.master_dict,fp)

        # clear out the master dict
        self.master_dict = {}

        selection = self.list_of_files_widget.curselection()
        self.list_of_files_widget.select_clear(selection)
        self.list_of_files_widget.select_set(selection[0]+1)
        self.cntlptlistbox.clearAllItems()
        self.updateImageCanvas()

        self.list_of_keypoints.delete(0,"end")
        
    def clearEntryText(self,event):
        self.idTextVar.set("")
        
    def addIdTag(self):
        print(f"{self.idTextVar.get()}")
        
    def mouseClick(self,event):
        if event.widget._name == 'image_canvas' and len(self.list_of_files_widget.curselection())!= 0:

            x = self.imgcanvas.canvasx(event.x)
            y = self.imgcanvas.canvasy(event.y)
            normList = []
            for each in self.keypoints:
                clickedPixel = (x,y)
                keypoint = each.pt
                normList.append(euclidean(clickedPixel,keypoint))
            
            minidx = normList.index(min(normList))

            self.highlightedTargetKeypoint = self.keypoints[minidx]
            self.drawkeypoint(self.highlightedTargetKeypoint,self.tempimgname)
    
    def drawkeypoint(self,keypoint,filename):
        img_copy = np.array(self.img)
        if len(img_copy.shape)!=3:
            img_copy = cv2.cvtColor(img_copy,cv2.COLOR_GRAY2BGR)

        img_with_blob = cv2.circle(img_copy, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size), (0,0,255), 3)
        img_with_blob = cv2.drawMarker(img_with_blob, (int(keypoint.pt[0]),int(keypoint.pt[1])),(0,255,255), markerType=cv2.MARKER_CROSS, markerSize=5, thickness=1, line_type=cv2.LINE_AA)
        
        cv2.imwrite(filename,img_with_blob)
        self.updateImageCanvas(filename=filename)
    
    def drawkeypointsandputtext(self,text,keypoint,filename):
        img_copy = np.array(self.img)
        if len(img_copy.shape)!=3:
            img_copy = cv2.cvtColor(img_copy,cv2.COLOR_GRAY2BGR)

        img_with_blob = cv2.circle(img_copy, (int(keypoint.pt[0]),int(keypoint.pt[1])), int(keypoint.size), (0,255,0), 3)
        img_with_blob = cv2.drawMarker(img_with_blob, (int(keypoint.pt[0]),int(keypoint.pt[1])),(0,255,255), markerType=cv2.MARKER_CROSS, markerSize=5, thickness=1, line_type=cv2.LINE_AA)
        img_with_blob = cv2.putText(img_with_blob,text.upper(), (int(keypoint.pt[0])+1,int(keypoint.pt[1])+1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,255,255), 1,1)
        cv2.imwrite(filename,img_with_blob)
        self.updateImageCanvas()

    def detectTargetsFromImages(self):
        
        keypointfilename = os.path.join(self.path_dir,f".{self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]}_keypoints")
        if not os.path.exists(keypointfilename):
            self.npimg = np.array(self.img)
            if len(self.npimg.shape) == 3:
                npimggray = cv2.cvtColor(self.npimg, cv2.COLOR_BGR2GRAY)
            else:
                npimggray = self.npimg
            
            # create Keypoint file
            keypointfile = open(keypointfilename,'w')
            keypointfile.close()
            
             # blurr the image
            npimggray = cv2.GaussianBlur(npimggray,(5,5),0)
            
            # Simple Blob detector

            blob_Detector_params = cv2.SimpleBlobDetector_Params()

            blob_Detector_params.blobColor = 255

            # Set Area filtering parameters 
            blob_Detector_params.filterByArea = True
            blob_Detector_params.minArea = 25
            blob_Detector_params.maxArea = 40000
  
            # Set Circularity filtering parameters 
            blob_Detector_params.filterByCircularity = False 
            blob_Detector_params.minCircularity = 0.9
  
            # Set Convexity filtering parameters 
            blob_Detector_params.filterByConvexity = True
            blob_Detector_params.minConvexity = 0.9
      
            # Set inertia filtering parameters 
            blob_Detector_params.filterByInertia = False
            blob_Detector_params.minInertiaRatio = 0.25

            # Set Threshhold
            blob_Detector_params.minThreshold = 0.9

            blob_Detector_params.minDistBetweenBlobs = 25

            # Create a detector with the parameters 
            blob_Detector = cv2.SimpleBlobDetector_create(blob_Detector_params) 

            self.keypoints = blob_Detector.detect(npimggray)

            self.plotallkeypointsforimage(self.keypoints,npimggray)

            keypointlist = []
            for keypoint in self.keypoints:
                keypointlist.append((keypoint.angle, keypoint.class_id, keypoint.octave, keypoint.pt, keypoint.response, keypoint.size ))

            with open(keypointfilename,'ab') as keypointfile:
                keypointfile.write(pickle.dumps(keypointlist))
            
        else:
            # read keypoints onto list
            self.keypoints = []
            keypointlist = pickle.load(open(keypointfilename,'rb'))
            for keypoint in keypointlist:
                self.keypoints.append(cv2.KeyPoint(angle=keypoint[0], class_id=keypoint[1], octave=keypoint[2], x=keypoint[3][0], y=keypoint[3][1], response=keypoint[4], size= keypoint[5]))

    def plotallkeypointsforimage(self, keypoints,image):

        img_copy = image.copy()

        for keypointidx in range(len(keypoints)):
            img_with_blob = cv2.circle(img_copy, (int(keypoints[keypointidx].pt[0]),int(keypoints[keypointidx].pt[1])), int(keypoints[keypointidx].size), (0,255,55), 2)
            img_with_blob = cv2.drawMarker(img_with_blob, (int(keypoints[keypointidx].pt[0]),int(keypoints[keypointidx].pt[1])),(255,0,0), markerType=cv2.MARKER_CROSS, markerSize=5, thickness=1, line_type=cv2.LINE_AA)
            img_with_blob = cv2.putText(img_with_blob,str(keypointidx), (int(keypoints[keypointidx].pt[0])+1,int(keypoints[keypointidx].pt[1])+1), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.2, (0,255,255), 1,1)
        cv2.imwrite( os.path.join(self.path_dir,f".{self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]}_allkeypoints.jpg"),img_with_blob)

                
    def recordTheTargetID(self):
        tagId  = self.idTextVar.get().upper()
        if tagId == "":
            tk.messagebox.showerror("showerror", "This field cannot be empty") 
            return
        
        self.idTextVar.set("")
        self.list_of_keypoints.insert("end", tagId)
        currentImagefilename = os.path.join(self.path_dir,self.list_of_files_widget.get(self.list_of_files_widget.curselection()))
        
        self.master_dict[self.count] = {}
        self.master_dict[self.count]['image'] = self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]
        self.master_dict[self.count]['keypoint-id'] = tagId.upper()
        self.master_dict[self.count]['row'] = self.highlightedTargetKeypoint.pt[1]
        self.master_dict[self.count]['col'] = self.highlightedTargetKeypoint.pt[0]
        self.count += 1

        if tagId.upper() in cntrlPts:
            self.cntlptlistbox.selectItems(tagId.upper())

        with open(os.path.join(self.path_dir,f".{self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]}_keypoints.txt"),'+a') as txtFile:
            txtFile.write(f"{tagId.upper()}\t{self.list_of_files_widget.get(self.list_of_files_widget.curselection()).split('.')[0]}\t{self.highlightedTargetKeypoint.pt[1]}\t{self.highlightedTargetKeypoint.pt[0]}\n")


        self.drawkeypointsandputtext(tagId,self.highlightedTargetKeypoint,currentImagefilename)

    def doubleclickbinder(self,event):
        pass

    def enterpressed(self,event):
        # lets generate an event
        self.recordTheTargetID()

    def scrollUsingMouse(self, event):
        self.imgcanvas.yview_scroll(event.delta,'units')

    #def __del__(self):
        #self.sqldb.commit()
        #self.sqldb.close()
  

def main():
    
    ui = UI()      


if __name__=='__main__':
    main()