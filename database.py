import sqlite3

with open('script.sql') as f:
    content = f.read()
    
    db = sqlite3.connect('bot.db')
    cur = db.cursor()
    cur.executescript(content)
    cur.close()

print('Done setting up database.')