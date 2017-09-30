import sqlite3
from pendulum import Pendulum

from db import db_config, db_subjects

sqlite.register_adapter(Pendulum, lambda val: val.isoformat(' '))

db = db_config.create_db_connection()

cls = db.execute('select * from Classes where id = ?', (class_id,)).fetchone()

def get_class(class_id):
	cls = db.execute('select * from Classes where id = ?', [class_id]).fetchone()
	ret = {
	    'id': cls[0],
	    'userid': cls[1],
	    'term': cls[2],
	    'subject': cls[3],
	    'module': cls[4],
	    'start_time': cls[5],
	    'end_time': cls[6],
	    'repeat': cls[7],
	    'location': cls[8]
	}
	
	ret['subject'] = db_subjects.get_subject(id=ret['subject'])
	ret['term'] = db_terms.get_terms(id=ret['term'])
	
	return ret
	