import sqlite3
from pendulum import Pendulum

from db import db_config

sqlite.register_adapter(Pendulum, lambda val: val.isoformat(' '))

db = db_config.create_db_connection()

def insert_term(user_id, name, start, end):
	if db.execute('select * from Terms where name = ? and user_id = ?', (name, user_id)).fetchone() is None:
		db.execute('insert into Terms null,?,?,?,?', [user_id, name, start, end]);
	else:
		return 0
	db.commit()
	return 1

def get_terms(id=None, user_id=None):
	terms = db.execute('select * from Terms where id = ? or user_id = ?', [id, user_id]).fetchall()
	return [{'id': t[0], 'user_id': t[1], 'name': t[2], 'start': user[3], 'end': user[4]} for t in terms]


def update_term(id, user_id=None, name=None, start=None, end=None):
	db.execute('update Terms set '\
			   'user_id = coalesce(?, user_id),'\
			   'name = coalesce(?, name),'\
			   'start = coalesce(?, start),'\
			   'end = coalesce(?, end)'\
			   'where id = ?', [user_id, name, start, end, id])
	db.commit()

def query(query, params):
	return db.execute(query, params)