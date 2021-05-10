# File: tree.py
# References:
#    http://hg.python.org/cpython/file/4e32c450f438/Lib/tkinter/ttk.py
#    http://www.tcl.tk/man/tcl8.5/TkCmd/ttk_treeview.htm#M79
#    http://svn.python.org/projects/python/branches/pep-0384/Demo/tkinter/ttk/dirbrowser.py

import os

from tkinter import *
from tkinter import ttk     #@Reimport

from demopanels import MsgPanel, SeeDismissPanel

# Constants for formatting file sizes
KB = 1024.0
MB = KB * KB
GB = MB * KB

class TreeDemo(ttk.Frame):
    
    def __init__(self, isapp=True, name='treedemo'):
        ttk.Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title('Tree Demo')
        self.isapp = isapp
        self._create_widgets()
        
    def _create_widgets(self):
        if self.isapp:
            MsgPanel(self, ["One of the new Tk themed widgets is a tree widget, which allows ",
                            "the user to browse a hierarchical data-set such as a file system. ",
                            "The tree widget not only allows for the tree part itself, but it ",
                            "also supports an arbitrary number of additional columns which can ",
                            "show additional data (in this case, the size of the files found ",
                            "on your file system). You can also change the width of the columns ",
                            "by dragging the boundary between them."])
            
            # SeeDismissPanel(self)
        
        self._create_demo_panel()
        
    def _create_demo_panel(self):
        demoPanel = Frame(self)
        demoPanel.pack(side=TOP, fill=BOTH, expand=Y)
        
        self._create_treeview(demoPanel)    
        self._populate_root()
                    
    def _create_treeview(self, parent):
        f = ttk.Frame(parent)
        f.pack(side=TOP, fill=BOTH, expand=Y)
        
        # create the tree and scrollbars
        self.dataCols = ('fullpath', 'type', 'size')        
        self.tree = ttk.Treeview(columns=self.dataCols, 
                                 displaycolumns='size')
        
        ysb = ttk.Scrollbar(orient=VERTICAL, command= self.tree.yview)
        xsb = ttk.Scrollbar(orient=HORIZONTAL, command= self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        
        # setup column headings
        self.tree.heading('#0', text='Directory Structure', anchor=W)
        self.tree.heading('size', text='File Size', anchor=W)
        self.tree.column('size', stretch=0, width=70)
        
        # add tree and scrollbars to frame
        self.tree.grid(in_=f, row=0, column=0, sticky=NSEW)
        ysb.grid(in_=f, row=0, column=1, sticky=NS)
        xsb.grid(in_=f, row=1, column=0, sticky=EW)
        
        # set frame resizing priorities
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)
        
        # action to perform when a node is expanded
        self.tree.bind('<<TreeviewOpen>>', self._update_tree)
        
    def _populate_root(self):
        # use current directory as root node
        self.path = os.getcwd()
        
        # insert current directory at top of tree
        # 'values' = column values: fullpath, type, size
        #            if a column value is omitted, assumed empty
        parent = self.tree.insert('', END, text=self.path,
                                  values=[self.path, 'directory'])
        
        # add the files and sub-directories
        self._populate_tree(parent, self.path, os.listdir(self.path))
                
    def _populate_tree(self, parent, fullpath, children):
        # parent   - id of node acting as parent
        # fullpath - the parent node's full path 
        # children - list of files and sub-directories
        #            belonging to the 'parent' node
        
        for child in children:
            # build child's fullpath
            cpath = os.path.join(fullpath, child).replace('\\', '/')
    
            if os.path.isdir(cpath):
                # directory - only populate when expanded
                # (see _create_treeview() 'bind')
                cid =self.tree.insert(parent, END, text=child,
                                      values=[cpath, 'directory'])
                
                # add 'dummy' child to force node as expandable
                self.tree.insert(cid, END, text='dummy')  
            else:
                # must be a 'file'
                size = self._format_size(os.stat(cpath).st_size)
                self.tree.insert(parent, END, text=child,
                                 values=[cpath, 'file', size])
                
    def _format_size(self, size):
        if size >= GB:
            return '{:,.1f} GB'.format(size/GB)
        if size >= MB:
            return '{:,.1f} MB'.format(size/MB)
        if size >= KB:
            return '{:,.1f} KB'.format(size/KB)
        return '{} bytes'.format(size)
                
    def _update_tree(self, event): #@UnusedVariable
        # user expanded a node - build the related directory 
        nodeId = self.tree.focus()      # the id of the expanded node
        
        if self.tree.parent(nodeId):    # not at root
            topChild = self.tree.get_children(nodeId)[0]
            
            # if the node only has a 'dummy' child, remove it and 
            # build new directory; skip if the node is already
            # populated
            if self.tree.item(topChild, option='text') == 'dummy':
                self.tree.delete(topChild)
                path = self.tree.set(nodeId, 'fullpath')
                self._populate_tree(nodeId, path, os.listdir(path))

if __name__ == '__main__':
    TreeDemo().mainloop()