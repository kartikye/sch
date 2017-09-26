from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import json, datetime
from db import db_config
import pendulum

scopes = ['https://www.googleapis.com/auth/calendar']

credentials = ServiceAccountCredentials.from_json_keyfile_name('scheduler-keys.json', scopes)
http = credentials.authorize(Http())
service = build('calendar', 'v3', http=http)

db = db_config.create_db_connection()

def create_calendar(user_id):
    calendar = {
        'summary': db.execute('select first_name from Users where user_id = '+ str(user_id)).fetchone()[0] + "'s Schedule",
        'timeZone': 'America/Los_Angeles'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    
    calendar_id = created_calendar['id']
    
    rule = {
        'scope': {
            'type': 'user',
            'value': db.execute('select email from Users where user_id = '+ str(user_id)).fetchone()[0],
        },
        'role': 'owner'
    }

    created_rule = service.acl().insert(calendarId=calendar_id, body=rule).execute()

    print(created_calendar)
    db.execute("update Users set calendar = ? where user_id = ?", (calendar_id, user_id))
    db.commit()
    return calendar_id


def delete_calendar(user_id):
    cal_id = db.execute('select calendar from Users where user_id = ?', (user_id,)).fetchone()[0];
    service.calendars().delete(cal_id).execute()

def get_near_events(calendar_id):
    events = service.events().list(calendarId=calendar_id).execute()
    print(events)
    return [event['summary'] for event in events['items']]