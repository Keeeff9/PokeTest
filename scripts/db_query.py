import sqlite3
import sys

conn = sqlite3.connect("instance/pokedex.db")
for row in conn.execute(sys.argv[1]).fetchall():
    print(row)
conn.commit()