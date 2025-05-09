import sqlite3

db = sqlite3.connect("database/database.db", check_same_thread=False)
cur = db.cursor()
