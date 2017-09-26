import sqlite3
from pendulum import Pendulum
from sqlite3 import register_adapter

register_adapter(Pendulum, lambda val: val.isoformat(' '))


def create_db_connection():
	return sqlite3.connect("schedule.db")


db = create_db_connection()

#create users
db.execute('create table if not exists Users (user_id integer primary key autoincrement, first_name text, last_name text, msg_id text, email text, password text, calendar text, other_calendars text)')

#create terms
db.execute('create table if not exists Terms (id integer primary key autoincrement, userid integer, name text, start date, end date)')

#create subjects
db.execute('create table if not exists Subjects (id integer primary key autoincrement, userid integer, term_id integer, subject text)')

#create classes
db.execute('create table if not exists Classes (id integer primary key autoincrement, userid integer, term_id integer, subject_id integer, module text, start_time text, end_time text, repeat text, location text)')

#create homework
db.execute('create table if not exists Homework (id integer primary key autoincrement, userid integer, term_id integer, subject_id integer, name text, due date, time_left integer)')

#create conversation
db.execute('create table if not exists Conversation (id integer primary key autoincrement, userid integer, msg_id text, status text)')

db.commit()
db.close()