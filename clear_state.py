import sqlite3
from db import db_config

db = db_config.create_db_connection()
db.execute("update Conversation set status='' where userid = 1")
#db.execute("delete from Terms where userid = 1")
#db.execute("delete from Subjects where userid = 1")
db.commit()
