#makeBoard.py
'''
Interface into make_pysol_board.py
Input is the index of the board to make
'''
import subprocess, sys
import time

try:
    index = sys.argv[1]
    if not 1 <= int(index) <= 1000000:
        print('Invalid index value')
        exit()
    cmd =['python2', 'make_pysol_board.py', '-F', '-t'] 
    output = 'test/board%s.txt'%index
    cmd += [index, 'black_hole']
    subprocess.run(cmd, stdout=open(output,'w'))
    '''
    The following is just an example of how to 
    capture stdout, without writing it to file
    or dumping it to the console.
    '''
    #proc = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    #text = proc.stdout
    #print('here it comes')
    #print(text)
except IndexError:
    print('Fatal: board index missing')


