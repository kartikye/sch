from pymessager.message import QuickReply
from db import db_config, db_users
from cal import cal
import requests, json, config
import pendulum
db = db_config.create_db_connection()

def handle():
    users = db.execute('select msg_id, calendar from Users').fetchall()
    for user in users:
        cal.get_near_events(user[1])
        