from __future__ import print_function, unicode_literals
import os
import os.path
from os import path
import glob
import time
import io
import tempfile
import re
import asyncio

import requests  # import requests to download urls
from tkinter import Tk, filedialog, Frame, LabelFrame, Entry, StringVar, Radiobutton,W,E,N,S, NSEW, Label, Listbox, CENTER, NO, END, OptionMenu, Button, Scrollbar,HORIZONTAL,VERTICAL
from tkinter import ttk

from jikanpy import Jikan  # import jikan for anime poster urls
from PIL import Image  # import pil for image conversions
from pprint import pprint

class anicon():
    def __init__(self):
        print("----------------------\n\n\n\nInitiation")
        self.ji = Jikan()
    def treefy(self,path):
        self.root = Tk()
        app_width = 820
        app_height = 740
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (app_width/2)
        y = (screen_height / 2) - (app_height/2)
        # window size and positioning
        self.root.geometry(f'{app_width}x{app_height}+{int(x/2)}+{int(y/2)}')
        self.root.title('Anicons | Stay Degenerate ')
        
        self.top_frame       = LabelFrame(self.root, text="Top level folder",padx =5 ,pady=5)
        self.top_frame       .grid(row=0,column=0,columnspan=4,padx =10 ,pady=10,sticky="NESW")
        
        self.tree_frame       = LabelFrame(self.root, text="Tree Structure",padx =5 ,pady=5)
        self.tree_frame       .grid(row=1,column=0,columnspan=4,padx =10 ,pady=10,sticky="NESW")
        
        self.top_lavel_text = StringVar()
        self.top_lavel_text.set("Chose your anime folder ...")
        self.top_label = Label(self.top_frame,textvar=self.top_lavel_text)
        self.top_label.grid(row=0 ,column=0)  
        
        self.choose_top_button = Button(self.top_frame, text='Choose Root', )
        self.choose_top_button.grid(row=0, column=3 , padx=30)
        
        # Treeview 
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.grid(row=0,column=0,sticky=NSEW)

        self.tree.heading('#0', text=path, anchor='w')
        
        abspath = os.path.abspath(path)
        self.ysb  = Scrollbar(self.tree_frame)
        self.ysb.grid(row=0,column=8,sticky=NSEW)
        self.ysb.config(command= self.tree.yview)
        
        self.xsb  = Scrollbar(self.tree_frame)
        self.xsb.grid(row=1,column=0,sticky=NSEW)
        self.xsb.config(command= self.tree.xview,orient=HORIZONTAL)
        
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)
        

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)
    


ani = anicon()
ani.treefy('./')
ani.root.mainloop()
print('Execution Finish\n\n\n\n----------------------')