# model.py Model for black hole
import random
import itertools
import subprocess
import re
import time
import os

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

pattern = re.compile(r'Move.*?([0-9]+).*?foundations')

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
    
class Model:
    '''
    The cards are all in self.deck, and are copied into the tableau piles
    All entries on the undo and redo stacks are in the form (source, target, n, f), where
        tableau piles are numbered 0 to 9 and foundations 10 to 17, 
        n is the number of cards moved, 
        f is a boolean indicating whether or not the top card of the source stack is flipped,
        except that the entry (0, 0, 10, 0) connotes dealing a row of cards. 
      '''
    def __init__(self):
        random.seed()
        self.deck = []
        self.undoStack = []
        self.redoStack = []
        self.createCards()
        self.tableau = [list() for _ in range(17) ]
        self.hole = [ ] 
        self.deal()

    def shuffle(self):
        for w in self.tableau:
            w.clear()
        self.hole[:] = []
        d = self.deck[1:]
        random.shuffle(d)
        self.deck[1:]=d

    def createCards(self):
        for rank, suit in itertools.product(ALLRANKS, SUIT_NAMES):
            self.deck.append(Card(rank, suit))

    def deal(self):
        assert len(set(self.deck)) == 52
        self.shuffle()
        for n, card in enumerate(self.deck[1:]):
            self.tableau[n%17].append(card)
        self.hole.append(self.deck[0])
        assert len(set(self.deck)) == 52
    
    def dealString(self):
        answer = 'Foundations: AS\n'
        for t in self.tableau:
            answer += t[0].code + ' ' + t[1].code + ' '+ t[2].code + '\n'
        return answer
        
print(os.getcwd())
prog = ['cat test/big.txt | ../black-hole-solve --game black_hole --rank-reach-prune --max-iters 750000'] 
#args= prog+['test/board1.txt']
model = Model()
PIPE = subprocess.PIPE
#proc = subprocess.Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
#proc.wait()
#print(trial, proc.poll())
#out = proc.stdout.read()
#time.sleep(60)
#proc.terminate()
#print('killed')
#out,err = proc.communicate()
#open('test/output%d'%trial, 'w').write(out)
proc = subprocess.Popen(prog, universal_newlines=True, stdout=PIPE, shell=True)
while True:
    status =  proc.poll()
    print('polling')
    if status is None:
        time.sleep(5)
    else:
        print('status', status)
        break
out = proc.stdout.read()
print(out)
soln=[int(s) for s in pattern.findall(out)]
print(soln)

