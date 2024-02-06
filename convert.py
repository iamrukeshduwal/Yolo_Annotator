# -*- coding: utf-8 -*-

import os
from os import walk, getcwd
from PIL import Image
import re


def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
    

def Convert2Yolo(mypath, outpath, project, classes):
    wd = getcwd()
    list_file = open('%s/log/%s_list.txt'%(wd, project), 'w')
    
    """ Get input text file list """
    txt_name_list = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        txt_name_list.extend(filenames)
        break
    # print(txt_name_list)
    
    """ Process """
    for txt_name in txt_name_list:
        # txt_file =  open("Labels/stop_sign/001.txt", "r")
        """ Open input text files """
        txt_path = mypath + txt_name
        print("Input:" + txt_path)
        txt_file = open(txt_path, "r")
        lines = txt_file.read().split('\n')   #for ubuntu, use "\r\n" instead of "\n"
        
        """ Open output text files """
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        txt_outpath = outpath + re.split('.jpg|.png',txt_name)[0]
        print("Output:" + txt_outpath)
        txt_outfile = open(txt_outpath, "w")
        
        
        """ Convert the data to YOLO format """
        ct = 0
        for line in lines:
            #print('lenth of line is: ')
            #print(len(line))
            #print('\n')
            elems = line.split(' ')
            if(len(elems) >= 2):
            #if(len(line) >= 2):
                ct = ct + 1
                print(line)
                elems = line.split(' ')
                print(elems)
                xmin = elems[0]
                xmax = elems[2]
                ymin = elems[1]
                ymax = elems[3]
                cls = elems[4]
                if cls not in classes:
                    exit(0)
                cls_id = classes.index(cls)
                print(elems[0])

                img_path = str('%s/Images/%s/%s'%(wd, project, os.path.splitext(txt_name)[0])+'.jpg')
                #t = magic.from_file(img_path)
                #wh= re.search('(\d+) x (\d+)', t).groups()
                im=Image.open(img_path)
                w= int(im.size[0])
                h= int(im.size[1])
                #w = int(xmax) - int(xmin)
                #h = int(ymax) - int(ymin)
                # print(xmin)
                print(w, h)
                print(float(xmin), float(xmax), float(ymin), float(ymax))
                b = (float(xmin), float(xmax), float(ymin), float(ymax))
                bb = convert((w,h), b)
                print(bb)
                
                txt_outfile.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    
        txt_outfile.close()
        txt_file.close()
        
        """ Save those images with bb into list"""
        if(ct != 0):
            list_file.write('%s/images/%s/%s\n'%(wd, cls, os.path.splitext(txt_name)[0]))
        else :
            os.remove(txt_outpath)
        
        print ("\n")
                    
    list_file.close()   

if __name__ == '__main__':
    mypath = "./Result/yeongju/"
    outpath = "./Result_YOLO/yeongju/"
    project = "yeongju"
    classes = ["pothole","patchdamaged","spalling"]
    Convert2Yolo(mypath, outpath, project, classes)  
