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
    user = db.execute('select first_name, timezone, email from Users where user_id = '+ str(user_id)).fetchone()
    print(user)
    calendar = {
        'summary': user[0] + "'s Schedule",
        'timeZone': user[1]
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    
    calendar_id = created_calendar['id']
    
    rule = {
        'scope': {
            'type': 'user',
            'value': user[2],
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
    try:
        cls = db_classes.get_class(class_id)
        user = db.execute('select timezone, calendar from Users where user_id = ?', (cls['userid'],)).fetchone()
        repeat = cls['repeat'].split(' ')
        r_string = ''
        switch = {
            'm': 'MO',
            't': 'TU',
            'w': 'WE',
            'th': 'TH',
            'f': 'FR',
            's': 'SA',
            'su': 'SU',
            '': ''
        }
        for r in repeat:
            r_string += switch[r] + ','
        
        r_string = r_string[0:-1]
        
        event = {
            'summary': cls['subject']['subject']+': '+cls['module'],
            'location': cls['location'],
            'start': {
                'dateTime': str(cls['term']['start'].at(int(cls['start_time'].split(':')[0]), int(cls['start_time'].split(':')[1]),0).timezone_(user[0]).in_tz('utc')),
                'timeZone': user[0],
            },
            'end': {
                'dateTime': str(cls['term']['start'].at(int(cls['end_time'].split(':')[0]), int(cls['end_time'].split(':')[1]), 0).timezone_(user[0]).in_tz('utc')),
                'timeZone': user[0]
            },
            'recurrence': [
                'RRULE:FREQ=WEEKLY;BYDAY='+r_string+';UNTIL='+cls['term']['end'].format('%Y%m%d') + 'T' + cls['term']['end'].format('%H%M%S') + 'Z'
            ],
        }
    
        event = service.events().insert(calendarId=user[1], body=event).execute()
        print(event)
        
        event_id = event['id']
        db_classes.set_event_id(class_id, event_id)
        return 1
    except:
        return 0
        
    #print 'Event created: %s' % (event.get('htmlLink'))