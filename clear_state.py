import sqlite3
from db import db_config
import sys, os


db = db_config.create_db_connection()
if len(sys.argv) > 1:
    db.execute("delete from Terms where userid = 1")
    db.execute("delete from Subjects where userid = 1")
    db.execute("delete from Classes where userid = 1")
db.execute("update Conversation set status='' where userid = 1")
db.commit()
os.system('python3 run.py')
