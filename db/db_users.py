from db import db_config

db = db_config.create_db_connection()

def insert_user(first_name, last_name, msg_id, password):
	if db.execute('select * from Users where msg_id = ?', (msg_id,)).fetchone() is None:
		cursor = db.execute('insert into Users(first_name, last_name, msg_id, password) values (?,?,?,?)', [first_name, last_name, msg_id, password]);
		i = cursor.lastrowid
		db.execute('insert into Conversation(userid, msg_id, status) values(?,?,?)', [i, msg_id, ''])
		db.commit()
		return cursor.lastrowid
	else:
		return -1
	

def get_user(id=None, msg_id=None):
	user = db.execute('select * from Users where id = ? or msg_id = ?', [id, msg_id]).fetchone()
	return {
		'id': user[0],
		'first_name': user[1],
		'last_name': user[2],
		'msg_id': user[3],
		'email': user[4],
		'password': user[5]
	}


def update_user(id, first_name=None, last_name=None, msg_id=None, password=None):
	db.execute('update Users set '\
			   'first_name = coalesce(?, first_name),'\
			   'last_name = coalesce(?, last_name),'\
			   'msg_id = coalesce(?, msg_id),'\
			   'email = coalesce?, email),'
			   'password = coalesce(?, password)'\
			   'where id = ?', [first_name, last_name, msg_id, password, id])
	db.commit()

def query(query, params):
	return db.execute(query, params)