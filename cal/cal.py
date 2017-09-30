from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import json, datetime
from db import db_config, db_classes
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
        'role': 'writer'
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
    events = service.events().list(calendarId=calendar_id, timeMax=pendulum.utcnow().add(minutes=15).to_rfc3339_string(), singleEvents=True, maxResults=2).execute()
    return events['items']
    
def test():
    id = 'nteed2v0b3cehcnfemu4kqubt4@group.calendar.google.com'
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId=id, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def add_class(class_id):
    cls = db_classes.get_class(class_id)
    event = {
        'summary': cls['subject']['subject']+': '+cls['module'],
        'location': cls['location'],
        'start': {
            'dateTime': '',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2015-05-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print 'Event created: %s' % (event.get('htmlLink'))