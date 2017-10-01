import sqlite3
from pendulum import Pendulum
from cal import cal

from db import db_config, db_subjects, db_terms

sqlite3.register_adapter(Pendulum, lambda val: val.isoformat(' '))

db = db_config.create_db_connection()

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
	    'location': cls[8],
	    'event_id': cls[9]
	}
	
	ret['subject'] = db_subjects.get_subject(id=ret['subject'])
	ret['term'] = db_terms.get_terms(id=ret['term'])
	
	return ret
	
def delete(class_id):
	cls = db.execute('select * from Classes where id = ?', [class_id]).fetchone()
	if cls[9]:
		cal.delete_class_event(cls[9])
	db.execute('delete from classes where id = ?',(class_id,))
	db.commit()
	
def set_event_id(class_id, event_id):
	db.execute('update Classes set event_id = ? where id = ?', (event_id, class_id))
	db.commit()
	