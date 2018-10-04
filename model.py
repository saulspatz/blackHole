# model.py Model for black hole
import random
import itertools 
import sys
import os
import subprocess
import re

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# RANKNAMES is a list that maps a rank to a string.  It contains a
# dummy element at index 0 so it can be indexed directly with the card
# value.

SUIT_NAMES = 'SHDC'
RANK_NAMES = ' A23456789TJQK'
if sys.version_info.major == 3:
    SUIT_SYMBOLS = ('\u2660','\u2665','\u2666','\u2663') 
else:
    SUIT_SYMBOLS =(u'\u2660'.encode('utf-8'),
                                    u'\u2665'.encode('utf-8'),
                                    u'\u2666'.encode('utf-8'),
                                    u'\u2663'.encode('utf-8'))
    
def cardCode(rank, suit):
    return RANK_NAMES[rank]+suit

class Card:
    '''
    A card is identified by its suit and rank.
    '''
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.color = 0 if suit in 'HD' else 1
        self.code =cardCode(rank, suit)

    def __repr__(self):
        return self.code

    def __str__(self):
        r = RANK_NAMES[self.rank]
        s = SUIT_SYMBOLS[SUIT_NAMES.index(self.suit)]
        return r+s

class Pile(list):
    def __initi__(self):
        list.__init__(self)
    
    def find(self, code):
        '''
        Is the card with the given code is in the pile?
        '''
        for idx, card in enumerate(self):
            if card.code == code:
                return True
        return False      
    
    def clear(self):
        self[:] = []
        
    
class Model:
    '''
    The cards are all in self.deck, and are copied into the tableau piles
    All entries on the undo and redo stacks are in the form (source, target, n, f), where
        tableau piles are numbered 0 to 9 and foundations 10 to 17, 
        n is the number of cards moved, 
        f is a boolean indicating whether or not the top card of the source stack is flipped,
        except that the entry (0, 0, 10, 0) connotes dealing a row of cards. 
      '''
    def __init__(self, parent):
        self.parent = parent
        self.solnPattern = re.compile(r'Move.*?([0-9]+).*?foundations')
        random.seed()
        self.deck = []
        self.undoStack = []
        self.redoStack = []
        self.createCards()
        self.tableau = [ Pile() for _ in range(17) ]
        self.hole = [ ] 
        self.solverProc = None
        
    def shuffle(self):
        for w in self.tableau:
            w.clear()
        self.hole[:] = []
        d = self.deck[1:]
        random.shuffle(d)
        self.deck[1:]=d
        self.solved=False

    def createCards(self):
        for rank, suit in itertools.product(ALLRANKS, SUIT_NAMES):
            self.deck.append(Card(rank, suit))
            
    def deal(self, shuffle=True):
        if shuffle:
            self.shuffle()
        for n, card in enumerate(self.deck[1:]):
            self.tableau[n%17].append(card)
        self.hole = [self.deck[0]]
        self.undoStack = []
        self.redoStack = []         
      
        # *** SIDE EFFECTS  ***
        # solve will set self.solverProc, self.board
        # and self.solution    
        if shuffle:
            self.solve()
   
    def move(self, k):
        '''
        Move top card from tableau[k] to black hole.
        Return True if the move is successful, else False

        '''
        pile = self.tableau[k]
        hole = self.hole
        try:
            if not self.canMove(k):
                return False
            hole.append(pile.pop())
            self.undoStack.append(k)
            return True
        except IndexError:
            return False
        
    def canMove(self, k):
        '''
        Can the top card of pile k be moved to the black hole?
        '''
        try:
            card =  self.tableau[k][-1]
        except IndexError:
            return False
        return abs(card.rank - self.hole[-1].rank)  in (1,12)
        
    def blocked(self):
        if self.won(): 
            return False
        return not any(self.canMove(k) for k in range(17)) 
        
    def won(self):
        return len(self.hole)==52 
    
    def undo(self):
        ''''
        Pop one record off the undo stack and undo the corresponding move.
        '''
        k = self.undoStack.pop()
        self.redoStack.append(k)
        self.tableau[k].append(self.hole.pop())
    
    def redo(self):
        ''''
        Pop a record off the redo stack and redo the corresponding move.
        ''' 
        k = self.redoStack.pop()
        self.undoStack.append(k)
        self.hole.append(self.tableau[k].pop())        
            
    def canUndo(self):
        return self.undoStack != []

    def canRedo(self):
        return self.redoStack != []  

    def restart(self):
        while self.canUndo():
            self.undo()
            
    def boardString(self):
        board = 'Foundations: AS\n'
        for t in self.tableau:
            board += '%s %s %s\n'%(t[0].code,t[1].code,t[2].code)
        return board
    
    def solve(self):
        try:
            self.solverProc.kill()
        except:
            pass
        self.board = self.boardString()
        cmd = os.path.join(self.parent.runDir,'black-hole-solve')
        args = 'echo '+'"'+self.board+'"' ' | ' +cmd+ ' '
        args += '--game black_hole --rank-reach-prune --max-iters 75000000'
        self.solverProc = subprocess.Popen(args, universal_newlines=True, 
                                           stdout=subprocess.PIPE, shell=True)
        
    def readSolution(self):
        proc = self.solverProc
        status = proc.poll()
        if status == None:
            return 'running'
        if status == 255:
            return 'unsolved'
        if status == 254:
            return 'intractable'
        if not self.solved:
            out = proc.stdout.read()
            pattern=self.solnPattern
            self.soln = [int(s) for s in pattern.findall(out)]
            self.solved = True
        for t in self.tableau:
            t.clear()
        self.deal(False)
        self.undoStack = []
        self.redoStack = list(reversed(self.soln)) 
        return ('solved')
    
    def saveGame(self):
        dirname = os.path.join(self.parent.runDir,'savedGames')
        length = 1+len([f for f in os.listdir(dirname) if f.startswith('board')])
        name = 'board%d.txt'%length
        filename = os.path.join(dirname, name)
        deck = self.deck
        with open(filename, 'w') as fout:
            fout.write('Foundations: AS\n')
            for c in range(1,18):
                for idx in range(c, 52, 17):
                    fout.write('%s '%(deck[idx].code))
                fout.write('\n')
