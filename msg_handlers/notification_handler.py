from pymessager.message import QuickReply
from db import db_config, db_users
from cal import cal
import requests, json, config
import pendulum
db = db_config.create_db_connection()
from run import client

sent = []

def handle():
    users = db.execute('select msg_id, calendar, timezone from Users').fetchall()
    for user in users:
        print(user, user[1])
        msg_id = user[0]
        if (user[1] == ''):
            return
        events = cal.get_near_events(user[1])
        if len(events) == 1:
            event_id = events[0]['id'] 
            if event_id not in sent and pendulum.parse(events[0]['start']['dateTime']) > pendulum.now(user[2]):
                sent.append(event_id)
                client.send_text(msg_id, 'Hi, you have '+events[0]['summary'] +' at ' + pendulum.parse(events[0]['start']['dateTime']).format('%I:%M %p'))
        elif len(events) > 1:
            to_send = []
            for event in events:
                if event['id'] not in sent and pendulum.parse(event['start']['dateTime']) > pendulum.now(user[2]):
                    to_send.append(event)
                    sent.append(event['id'])
            if len(to_send) > 0:
                client.send_text(msg_id, 'Hi, you have a few events coming up: '+ ','.join([e['summary'] for e in to_send]))
        
        