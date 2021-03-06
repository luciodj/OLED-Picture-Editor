#!usr/bin/env python
#
# OLED display picture editor
#
import sys
from Tkinter import *
from itertools import imap
from os import path
import tkMessageBox
#
# window definition
#
class EditorWindow():

    def __init__(self, parent = None, name=''):
        win = Tk()
        win.title( 'OLED Picture Editor')
        win.protocol( 'WM_DELETE_WINDOW', self.cmdQuit)	# intercept Ctrl_Q and Close Window button
        self.win = win

        sf = 8
        self.sf = sf
        wx = 96; wy = 40
        self.wx = wx; self.wy = wy
        self.array = [ 0 for x in xrange( wx * wy / 8)]
        self.modified = False

        Label( win, text='File:').grid( padx=10, pady=1, row=1, column=0, sticky=W)

        self.filename = StringVar()	
        self.filename.set( name)
        e = Entry( win, width=64, takefocus=YES, textvariable = self.filename)
        e.grid(  padx=10, pady=10, row=1, column=1, sticky=W)
        e.focus_set()   # take over input from other windows, select address field
        e.icursor(END)  # set cursor after last digit

        Button( win, text='Load', takefocus=YES, command=self.cmdLoad ).grid( padx=10, pady=10, row=1, column=2)
        Button( win, text='Import', takefocus=YES, command=self.cmdImport ).grid( padx=10, pady=10, row=1, column=3)

        #------- editor canvas ----------------------------
        brd = 2
        self.brd = brd
        graph = Canvas( win, width=(wx)*sf, height=(wy)*sf, relief='flat', bd=brd, bg='gray')
        graph.grid( padx=10, row=2, columnspan=4)
        graph.bind( '<Button-1>', self.cmdToggle)   # capture mouse button inside canvas
        self.graph = graph

        if name != '':
            self.cmdLoad() 
        self.drawPicture()

        #------- button Close -----------------------------------
        # Button( win, text='FlipX', takefocus=YES, command=self.cmdFlipX ).grid( padx=10, pady=10, row=3, column=0)
        Button( win, text='Save', takefocus=YES, command=self.cmdSave ).grid( padx=10, pady=10, row=3, column=2)
        Button( win, text='Close', takefocus=NO, command=self.cmdQuit).grid( padx=10, pady=10, row=3, column=3)

    #-------------------- Graphs methods
    def drawPicture( self):
        for y in xrange( self.wy):
            for x in xrange( self.wx):
                self.drawPixel( x, y)       

    def getPixel( self, x, y):
        return self.array[ (y>>3)*self.wx + x] & (1<< (y&7)) != 0

    def setPixel( self, x, y):
        self.array[ (y>>3)*self.wx + x] |= (1 << ( y&7))
        self.drawPixel( x, y)

    def invPixel( self, x, y):
        self.array[ (y>>3)*self.wx + x] ^= (1 << ( y&7))
        self.drawPixel( x, y)

    def drawPixel( self, x, y):
        sf = self.sf
        brd = 1+self.brd
        if  self.getPixel( x, y):
            self.graph.create_rectangle( brd+x*sf, brd+y*sf, brd+(x+1)*sf, brd+(y+1)*sf, fill = 'white')
        else:
            self.graph.create_rectangle( brd+x*sf, brd+y*sf, brd+(x+1)*sf, brd+(y+1)*sf, fill = 'black')

    def cmdToggle( self, event):
        x = int( (self.graph.canvasx( event.x)-1-self.brd)/self.sf) 
        y = int( (self.graph.canvasy( event.y)-1-self.brd)/self.sf) 
        if x < self.wx and y < self.wy:
            self.invPixel( x, y)
            self.modified = True

    def cmdFlipX( self):
        for y in xrange( 0, self.wy/8*self.wx, self.wx):
            for x in xrange( self.wx/2):
                xo = self.wx-x-1
                self.array[ x + y], self.array[ xo + y] = self.array[ xo + y], self.array[ x + y]
        self.drawPicture()
        self.modified = True

    def cmdImport( self):
        THR = THG = THB = 1
        if self.modified:
            if not tkMessageBox.askokcancel( 'Import', 'Unsaved changes will be lost!\n Are you sure?', icon='warning'):            
                return
        filename = self.filename.get()
        base, ext = path.splitext( filename)
        if ext == '': ext = '.gif'
        if ext != '.gif': 
            tkMessageBox.showinfo( 'Error', 'Only GIF files can be imported!', icon='warning')
            return
        filename = base + ext
        try:
            photo = PhotoImage( file=filename)
        except: print 'Could not import image file:', filename
        else:
            wx = min( self.wx, photo.width()); wy = min( self.wy, photo.height())
            for y in xrange( wy):
                for x in xrange( wx):
                    r, g, b = imap( lambda x: int(x), photo.get( x, y).split())
                    if (r, g, b) == (0,0,0) or (r, g, b) == (255, 255, 255): continue  # discard transparent and white
                    if r > THR or g > THG or b > THB : self.setPixel( x, y)
            print 'File %s imported successfully' % filename
            self.modified = False

    def cmdLoad( self):
        if self.modified:
            if not tkMessageBox.askokcancel( 'Load', 'Unsaved changes will be lost,\n are you sure?', icon='warning'):            
                return
        i = 0
        last = (self.wx * self.wy/8) 
        try:
            with open( self.filename.get()) as f:
                ch = f.read( 1)
                while ch != '{': ch = f.read(1)
                while i < last:
                    ch = f.read(1)
                    while ch < '0' : ch = f.read( 1)
                    if ch != '0': break  
                    s = f.read( 3)
                    try: self.array[i] = int( '0'+s, base=16)
                    except ValueError: break
                    i += 1 
                else: 
                    print 'File loaded successfully'
                    self.drawPicture()
                    self.modified = False
                    return 
                print 'File format could not be recognized!'
        except IOError: print 'File %s not found' % self.filename.get()

    def cmdSave( self):
        filename = self.filename.get()
        if path.isfile( filename): 
            if not tkMessageBox.askokcancel('Save', 'File %s already exist!\n Overwrite?'% filename):            
                return            
        base, ext = path.splitext( filename)
        if ext == '': ext = '.c'
        if ext != '.c':
            tkMessageBox.showinfo( 'Error', 'Only .c files can be generated!', icon='warning')
            return
        filename = base + ext
        try:
            with open( filename, "wt") as f:
                f.write( '/*\n')
                f.write( ' *  OLED display image \n')
                f.write( ' *  %s x %s \n' % ( self.wx, self.wy))
                f.write( ' */ \n')
                f.write( '#include "mcc_generated_files/mcc.h"\n\n')
                f.write( 'const uint8_t %s[]={ \n' % base)
                for x in xrange( 0, self.wx * self.wy/8, 16):
                    for k in xrange( 16):
                        f.write( '0x%02x, '% self.array[ x + k])
                    f.write( '\n')
                f.write( '};\n')
                self.modified = False
        except IOError: print 'Cannot write file:', filename

    def cmdQuit( self):
        if self.modified: 
            if  not tkMessageBox.askokcancel("Quit", "There are unsaved changes,\n are you sure?"): return
        self.win.quit()

if __name__ == '__main__': 
    filename = ''
    if len( sys.argv) > 1: filename = sys.argv[1]
    EditorWindow( name = filename)
    mainloop()
