import json

#from httplib2 import Http

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/calendar	']

credentials = ServiceAccountCredentials.from_json_keyfile_name('/scheduler-keys.json', scopes)

#http = credentials.authorize(httplib2.Http())
#service = discovery.build('calendar', 'v3', http=http)

#now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#print('Getting the upcoming 10 events')
#eventsResult = service.events().list(
#calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
#events = eventsResult.get('items', [])


#print(response)