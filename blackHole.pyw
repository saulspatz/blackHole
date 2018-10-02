# blackHole.pyw
'''
Black hole solitaire
'''
import model
from view import View
try:
    import tkinter as tk
    from tkinter.messagebox import showerror, showinfo, askokcancel
except ImportError:
    import Tkinter as tk
    from tkMessageBox import showerror, showinfo, askokcancel
import sys, os
import  subprocess

helpText = '''
This program implements Black Hole solitaire.

OBJECTIVE
The game is played with a deck of 52 cards.\
The objective in each game is to move all cards to a single pile.


SETUP
There are 17 tableau piles of 3 cards each and a central foundation  pile, \
the "black hole," initially containing the Ace of Spades.

MOVING CARDS
The cards in the the top cards of the tableau piles \
are available for play.  A card can be move to the black hole if it differs in rank \
by one from the card currently on top of the black hole.  An Ace is both high and \
low, so that the ranks are cyclic.  Chaning direction is permitted, so you can
put a 4 on top of a 5 and then a 5 on toip of the 4.

Suits are ignored.

BUTTONS
The "Undo" and Redo" buttons are self-explanatory.  \
The "Restart" button puts the game back to the beginning, but you can \
still redo all your moves. 

'''        
class BlackHole:
    def __init__(self):
        self.model = model.model
        self.view = View(self, self.quit)
        self.makeHelp()
        self.makeMenu() 
        self.view.start()      #  start the event loop

    def deal(self):
        model = self.model
        model.deal()
        self.view.show()

    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.title("Black Hole Help")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(f, height=30, width = 80, wrap=tk.WORD)
        text['font'] = ('helevetica', 14, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NSEW')
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(row=1, column=0)
        f.grid(sticky='NSEW')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT,helpText)

    def makeMenu(self):
        top = self.view.menu

        game = tk.Menu(top, tearoff=False)
        game.add_command(label='New', command=self.deal)
        game.add_command(label='Help', command = self.showHelp)  
        game.add_command(label='Quit', command=self.quit)
        top.add_cascade(label='Game', menu=game)     

    def notdone(self):
        showerror('Not implemented', 'Not yet available') 

    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
        
    def quit(self):
        self.view.root.quit()

if __name__ == "__main__":
    BlackHole()
