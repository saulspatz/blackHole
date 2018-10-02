from sqlite3 import *

conn =connect('test/bhs.db')
cursor = conn.cursor()
cursor.execute("SELECT idx, num_checked FROM bhs_runs WHERE status = 'S'")
solved=cursor.fetchall()
solved = sorted(solved, key = lambda x:x[1], reverse = True)
with open ('test/solved.txt','w') as fout:
    for sol in solved:
        fout.write('%d %d\n'%sol)
conn.close()
