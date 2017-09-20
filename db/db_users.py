from db import db_config

db = db_config.create_db_connection()

def insert_user(first_name, last_name, email, password):
	if db.execute('select * from Users where email = ?', (email,)).fetchone() is None:
		db.execute('insert into Users(first_name, last_name, email, password) values (?,?,?,?)', [first_name, last_name, email, password]);
	else:
		return 0
	db.commit()
	return 1

def get_user(id=None, email=None):
	user = db.execute('select * from Users where id = ? or email = ?', [id, email]).fetchone()
	return {
		'id': user[0],
		'first_name': user[1],
		'last_name': user[2],
		'email': user[3],
		'password': user[4]
	}


def update_user(id, first_name=None, last_name=None, email=None, password=None):
	db.execute('update Users set '\
			   'first_name = coalesce(?, first_name),'\
			   'last_name = coalesce(?, last_name),'\
			   'email = coalesce(?, email),'\
			   'password = coalesce(?, password)'\
			   'where id = ?', [first_name, last_name, email, password, id])
	db.commit()

def query(query, params):
	return db.execute(query, params)