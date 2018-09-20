# view.py
'''
The visual interface for black hole solitaire.
The view knows about the model, but not vice versa
The canvas widget is used for both view and controller.
'''
import sys, os, itertools, time
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk
    import tkMessageBox as messagebox
from model import SUIT_NAMES, RANK_NAMES, ALLRANKS, SUIT_SYMBOLS, Card


CARDWIDTH = 85
CARDHEIGHT = 128
OFFSET = 23
MARGIN = 10
XSPACING = CARDWIDTH + 3*MARGIN
YSPACING = CARDHEIGHT + 6*MARGIN

BACKGROUND = '#070'
PILEFILL = 'OliveDrab4' # fill color of piles
TEXT = 'yellow'              # button text color
BUTTON = 'forest green'

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

SUIT_FONT=("Times", "48", "bold")

imageDict = {}   # hang on to images, or they may disappear!

class ButtonBar(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self,parent, bg=BACKGROUND, bd=0, highlightthickness=0)
        self.configure(height=5*MARGIN,width=6*XSPACING)
        width=int(self['width'])
        self.makeButton(width//2-12*MARGIN, 'undo')
        self.makeButton(width//2-4*MARGIN, 'redo')
        self.makeButton(width//2+4*MARGIN, 'restart')
        self.place(in_=parent, relx=.5,y=0,anchor=tk.N)    

    def makeButton(self, left, text):
        self.create_oval(left, MARGIN, left+6*MARGIN, 4*MARGIN, fill=BUTTON, outline=BUTTON, tag = text)
        self.create_text(left+3*MARGIN,2.5*MARGIN,text=text.title(),fill=TEXT,tag=text,anchor=tk.CENTER)

class View: 
    '''
    Cards are represented as canvas image iitems,  displaying either the face
    or the back as appropriate.  Each card has the tag "card".  This is 
    crucial, since only canvas items tagged "card" will respond to mouse
    clicks.
    '''
    def __init__(self, parent, quit, **kwargs):
        # quit is function to call when main window is closed
        self.parent = parent          # parent is the Black Holel application
        self.model =  parent.model
        self.root = root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', quit)
        width = 5*MARGIN+5*XSPACING
        self.root.wm_geometry('%dx850-10+10'%width)
        root.title("Black Hole Solitaire")

        root.minsize(width=width, height=500)
        root.maxsize(width=width, height=2500)
        self.menu = tk.Menu(root)         # parent constructs actual menu         
        root.config(menu=self.menu)                 
        self.tableau = []           # NW corners of the tableau piles
        x = 4*MARGIN
        y = 6* MARGIN
        for k in range(5):
            self.tableau.append((x, y))
            x += XSPACING
        for row in range(3):
            y += YSPACING
            x = 4*MARGIN
            for _ in range(2):
                self.tableau.append((x, y))
                x += XSPACING
            x += XSPACING
            for _ in range(2):
                self.tableau.append((x, y))
                x += XSPACING
        x = 4*MARGIN + 2*XSPACING
        y = 6*MARGIN + 1.5*YSPACING
        self.hole = (x,y)
        canvas = self.canvas = tk.Canvas(root, bg=BACKGROUND, cursor=DEFAULT_CURSOR, 
                                                             bd=0, highlightthickness=0, width = width)
        canvas.pack(expand=tk.YES, fill=tk.Y)
        #width = kwargs['width']
        #height = kwargs['height']

        self.loadImages()
        self.createCards()
        canvas.tag_bind("card", '<Double-Button-1>', self.onDoubleClick)

        for t in self.tableau:
            canvas.create_rectangle(t[0], t[1], t[0]+CARDWIDTH, t[1]+CARDHEIGHT, 
                                                    fill=PILEFILL, outline=PILEFILL)
        x,y = self.hole
        canvas.create_rectangle(x, y, x+CARDWIDTH, x+CARDHEIGHT, 
                                                    fill=PILEFILL, outline=PILEFILL)
        
        self.buttons = ButtonBar(canvas)
        self.buttons.tag_bind('undo', '<ButtonPress-1>', self.undo)
        self.buttons.tag_bind('redo', '<ButtonPress-1>', self.redo)
        self.buttons.tag_bind('restart', '<ButtonPress-1>', self.restart)
        self.show()

    def start(self):
        self.root.mainloop()

    def loadImages(self):
        PhotoImage = tk.PhotoImage
        cardDir = os.path.join(os.path.dirname(sys.argv[0]), 'cards') 
        for suit, rank in itertools.product(SUIT_NAMES, ALLRANKS):
            face = PhotoImage(file = os.path.join(cardDir, RANK_NAMES[rank]+suit+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas    
        for card in model.deck:
            c = canvas.create_image(-200, -200, image = None, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%s'%card.code, c)

    def showTableau(self, k):
        '''
        Display tableau pile number k
        '''
        x, y = self.tableau[k]
        canvas = self.canvas
        for card in self.model.tableau[k]:
            tag = 'code%s'%card.code
            canvas.coords(tag, x, y)
            foto = imageDict[card.rank, card.suit]
            y += OFFSET
            canvas.itemconfigure(tag, image = foto)
            canvas.tag_raise(tag) 
            
    def showHole(self):
        '''
        Display black hole
        '''
        x, y = self.hole
        canvas = self.canvas
        card = self.model.hole[-1]
        tag = 'code%s'%card.code
        canvas.coords(tag, x, y)
        foto = imageDict[card.rank, card.suit]
        canvas.itemconfigure(tag, image = foto)
        canvas.tag_raise(tag) 

    def show(self):
        model = self.model
        canvas = self.canvas
        for k in range(17):
            self.showTableau(k)
        self.showHole()
        if model.canUndo():
            self.enableUndo()
        else:
            self.disableUndo()
        if model.canRedo():
            self.enableRedo()
        else:
            self.disableRedo()
        canvas.update_idletasks()
        if model.blocked():
            messagebox.showinfo('Blocked','No more moves',parent=self.canvas)

    def onDoubleClick(self, event):
        '''
        Respond to doublle click on tableau pile.  
        Clicks on the black hole are ignored.
        '''
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = tag[4:]             # code of the card clicked
        for k, p in enumerate(model.tableau):
            if p.find(code):
                break
        else:       # loop else
            return
        if model.move(k):
            self.show()
            
    def undo(self, event):
        self.model.undo()
        self.show()

    def redo(self, event):
        self.model.redo()
        self.show()  

    def restart(self, event):
        self.model.restart()
        self.show()

    def disableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.HIDDEN)

    def disableUndo(self):
        for item in ('undo', 'restart'):
            self.buttons.itemconfigure(item, state=tk.HIDDEN)

    def enableRedo(self):
        self.buttons.itemconfigure('redo', state=tk.NORMAL)

    def enableUndo(self):
        for item in ('undo', 'restart'):
            self.buttons.itemconfigure(item, state=tk.NORMAL)

    def wm_delete_window(self):
        self.root.destroy()

    def done(self, num):
        self.root.destroy()    
