import sqlite3
from pendulum import Pendulum

from db import db_config

db = db_config.create_db_connection()

def get_subject(id=None, subject=None):
    subject = db.execute('select * from Subjects where id = ? or subject = ?', (id, subject)).fetchone()
    print(subject)
    subject = {
        'id': subject[0],
        'userid': subject[1],
        'term_id': subject[2],
        'subject': subject[3]
    }
    return subject