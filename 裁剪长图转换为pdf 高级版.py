# coding=utf-8


import sys      # 给保存pdf使用
from PIL import Image   # 要装模组 pip install pillow    给保存pdf使用
from tkinter import Tk       # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename  
from pathlib import Path # 地址转string使用
import os #建立文件夹使用
from tkinter import messagebox
from sys import exit #用来给exit函数全局使用
import send2trash #用来删除文件
import time #用来计时
import tkinter as tk
import fitz
from PIL import Image


def AskRatio():
    # Create a new window
    window = tk.Toplevel()

    # Add a label to the window
    label1 = tk.Label(window, text="Since some times you may want to set the first page ratio different\n from the rest, you know what i'm saying ,\nso enter two ratios, thats it (enter the page ratio), \nBTW you can use mac preview app to draw to find the ratio\n")
    label1.pack()

    # Add another label to the window for the first expression
    label2 = tk.Label(window, text="Enter the first ratio (e.g. height/width):")
    label2.pack()

    # Add an input field to the window for the first expression
    entry1 = tk.Entry(window)
    entry1.pack()

    # Add another label to the window for the second expression
    label3 = tk.Label(window, text="Enter the second ratio (e.g. height/width):")
    label3.pack()

    # Add an input field to the window for the second expression
    entry2 = tk.Entry(window)
    entry2.pack()

    # Add a button to the window to submit the expressions
    def submit():
        global var1, var2
        expression1 = entry1.get()
        expression2 = entry2.get()
        var1a, var1b = expression1.split('/')
        var2a, var2b = expression2.split('/')
        var1 = float(var1a.strip()) / float(var1b.strip())
        var2 = float(var2a.strip()) / float(var2b.strip())
        window.destroy()

    button = tk.Button(window, text="Submit", command=submit)
    button.pack()

    # Add a default button to the window to assign var1 and var2 to the calculated result
    def default():
        global var1, var2
        var1 = 297/210
        var2 = 297/210
        window.destroy()

    default_button = tk.Button(window, text="Default", command=default)
    default_button.pack()

    # Call the submit function when the Enter key is pressed
    def on_key_press(event):
        if event.keysym == 'Return':
            submit()

    entry2.bind('<Key>', on_key_press)

    # Calculate the x and y coordinates of the window to center it on the screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)

    # Set the window's position and run it
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    window.wait_window(window)

    return var1, var2



if __name__ == '__main__':
    # 弹出选择文件窗口选取文件路径
    Tk().withdraw()              # we don't want a full GUI, so keep the root window from appearing
    filepath = askopenfilename() # show an "Open" dialog box and return the path to the selected file

    #问裁剪比例
    ratio1, ratio2 = AskRatio()

    #排除非图片
    filepathSTR = Path(filepath)
    suffix = str(filepathSTR.suffix)
    if (suffix==".png" or suffix==".jpg" or suffix==".jpeg"):
        # 新建文件夹
        newfolder = str(filepathSTR.parent) + "/"+ str(filepathSTR.stem)+"_cut"
        try:
            os.makedirs(newfolder)
        except:
            pass
        tosuffix = suffix
    elif (suffix==".pdf"):
        # 新建文件夹
        newfolder = str(filepathSTR.parent) + "/"+ str(filepathSTR.stem)+"_cut"
        try:
            os.makedirs(newfolder)
        except:
            pass
        tosuffix = ".png"
    elif (suffix==""):   #这里是如果弹窗选文件按了取消就直接退出，这招妙！！防止了error弹窗！！！
        exit()
    else:
        #msgbox
        messagebox.showwarning("Not pdf or image!", "Not pdf or image?")
        exit()

    #获取img
    if (suffix==".png" or suffix==".jpg" or suffix==".jpeg"):
        im = Image.open(filepath)
    elif (suffix==".pdf"):
        # Open the PDF file
        with fitz.open(filepath) as pdf:
            # Check if there's only one page
            if len(pdf) != 1:
                messagebox.showwarning("PDF file must have only one page.", "PDF file must have only one page.")
                exit()
            else:
                # Select the first page of the PDF
                page = pdf[0]
                # delete annotation
                for annot in page.annots():
                    page.delete_annot(annot)
                # Render the page as a PNG image
                pix = page.get_pixmap(alpha=False)
                # Convert the image to a PIL object
                im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
    # 裁剪长图
    imlist=[]
    i=1
    newwidth = im.width
    newheight = im.width * ratio1
    newheightpos2 = newheight * 1
    while newheightpos2 < im.height:
        newheightpos1 = newheight * (i - 1)
        newheightpos2 = newheight * i
        if i == 1:
            ratio = ratio1  # Use a different ratio for the first image
        else:
            ratio = ratio2  # Use a different ratio for the rest of the images
        newheight = newwidth * ratio
        croppedIm = im.crop( (0, newheightpos1, newwidth, newheightpos2) )
        # 地址转string  比如以下给名字标号
        new = str(filepathSTR.parent) + "/"+ str(filepathSTR.stem)+"_cut" + "/" + str(filepathSTR.stem) +"_%d" + str(tosuffix)      #双杠其中一杠是转义
        croppedIm.save(new%i)

        #存入pdf（先存到变量里）
        if(i==1):
            im1 = Image.open(new%i).convert('RGB')
        else:
            globals()['im%s'%i] = Image.open(new%i).convert('RGB')   # -----写到list
            k=globals()['im%s'%i]
            imlist.append(k)
        i+=1

    # 存入pdf
    PDFpath = str(filepathSTR.parent) + "/"+ str(filepathSTR.stem)+"_cut" + ".pdf"
    im1.save(PDFpath, save_all=True, append_images=imlist)  # -----一起存入pdf

    #提示完成
    messagebox.showwarning("Done! The folder automatically created never mind, it'll delete in 5 seconds!", "Done")

    # 删掉裁剪的图
    time.sleep(5)
    thefolder = str(filepathSTR.parent) + "/"+ str(filepathSTR.stem)+"_cut" 
    send2trash.send2trash(thefolder)
