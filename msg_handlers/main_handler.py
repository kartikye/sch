from run import client
from pymessager.message import QuickReply, ActionButton, WebviewType, ButtonType
from db import *
import requests, json, config
import pendulum
db = db_config.create_db_connection()
from cal import cal
from msg_handlers import responses
import re

responses = responses.responses

states = {}

def loud_print(s):
    print('###############################################')
    print(s)
    print('###############################################')

def handle(message):
    msg_id = message['sender']['id']
    text = message['message']['text']
    
    if  db.execute('select * from Users where msg_id = ?', (msg_id,)).fetchone() is None:
        #data = json.loads(requests.get('https://graph.facebook.com/v2.6/'+msg_id+'?fields=first_name,last_name&access_token='+config.facebook_access_token).text)
        data = client.get_user_data(msg_id)
        db_users.insert_user(data['first_name'], data['last_name'], msg_id, '')
        update_state(msg_id, 'setup#0')
        client.send_text(msg_id, responses['setup']['greet'].format(data['first_name']))
        return
    
    status = db.execute('select status from Conversation where msg_id = ?', (msg_id,)).fetchone()[0]
    
    #Check for mistake 

    if 'mistake' in message['message']['nlp']['entities'] and message['message']['nlp']['entities']['mistake'][0]['confidence'] > .9:
        if message['message']['nlp']['entities']['mistake'][0]['value'] == 'fuck':
            client.send_text(msg_id, responses['cancel']['insult'])
        client.send_text(msg_i, responses['cancel']['try_again'])
        return
    if 'exit' in message['message']['nlp']['entities'] and message['message']['nlp']['entities']['exit'][0]['confidence'] > .9:
        client.send_text(msg_id, responses['cancel']['exit'])
        update_state(msg_id, '')
        return

    switch = {
        '' : no_status,
        'setup': setup,
        'add.term': add_term,
        'add.subject': add_subject,
        'add.class': add_class,
        'add.task': add_task,
        'report.issue': report_issue
    }
    
    switch[status.split('#')[0]](message, msg_id, text, status)
    
def no_status(message, msg_id, text, status):
    message = message['message']
    entities = message['nlp']['entities']
    
    print(entities)
    
    if 'action' in entities:
        if message['nlp']['entities']['action'][0]['value'] == 'add':
            do_add(message, msg_id, text)
    elif 'help' in entities:
        do_help(message, msg_id, text)
    elif 'report_issue' in entities:
        do_report_issue(message, msg_id, text)
        
def do_add(message, msg_id, text):
    print('do_add')
    
    item =  message['nlp']['entities']['item'][0]['value']
    if item == 'term':
        update_state(msg_id, 'add.term#1')
        client.send_text(msg_id, responses['term']['name'])
    elif item == 'subject':
        if len(db.execute('select Terms.name from Terms join Users on Users.user_id = Terms.userid where Users.msg_id = ?', (msg_id,)).fetchall()) == 0:
            client.send_text(msg_id, responses['term']['no_term'])
            return
        update_state(msg_id, 'add.subject#1')
        client.send_text(msg_id, responses['subject']['what'])
    elif item == 'class':
        ask_to_add_class(msg_id)
    elif item == 'homework' or item == 'task':
        ask_to_add_task(msg_id)
    elif item == 'activity':
        pass
    elif item == 'meeting':
        i = 1/0
    else:
        pass
    
def setup(message, msg_id, text, status):
    message = message['message']
    step = int(status.split('#')[1])
    print()
    if step == 0:
        if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", text) != None:
            update_state(msg_id, 'setup#1')
            if msg_id not in states:
                states[msg_id] = {}
            if 'setup' not in states[msg_id]:
                states[msg_id]['setup'] = {}
            states[msg_id]['setup']['email'] = text
            ask_affirmation(msg_id, 'Is '+text+' correct?')
        else:
            client.send_text(msg_id, [responses['emoji']['sad'], ['email']['invalid'].format(text)])
    if step == 1:
        if 'affirmation' in message['nlp']['entities']:
            db.execute('update Users set email = ? where msg_id = ?', (states[msg_id]['setup']['email'], msg_id))
            db.commit()
            update_state(msg_id, 'setup#2')
            client.send_text(msg_id, responses['setup']['city'])
        else:
            update_state(msg_id, 'setup#0')
            client.send_text(msg_id, ':(')
            client.send_text(msg_id, responses['setup']['reenter_email'])
    if step == 2:
        try:
            coordinates = json.loads(requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+text+',+CA&sensor=false').text)['results'][0]['geometry']['location']
            timezone = json.loads(requests.get('https://maps.googleapis.com/maps/api/timezone/json?location='+str(coordinates['lat'])+','+str(coordinates['lng'])+'&timestamp='+str(pendulum.now().int_timestamp)+'&sensor=false').text)['timeZoneId']
        except Exception as e:
            print(e)
            client.send_text(msg_id, responses['setup']['timezone_error'])
            return
        db.execute('update Users set timezone = ? where msg_id = ?', (timezone, msg_id))
        db.commit()
        cal.create_calendar(db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0])
        client.send_text(msg_id, responses['setup']['done'])
        update_state(msg_id, 'add.term#1')
        client.send_text(msg_id, responses['setup']['start'])
            
            
#Add a term
def add_term(message, msg_id, text, status):
    step = int(status.split('#')[1])
    if step == 1:
        if msg_id not in states:
            states[msg_id] = {}
        if 'term' not in states[msg_id]:
            states[msg_id]['term'] = []
            states[msg_id]['term'].append(text)
        update_state(msg_id, 'add.term#2')
        client.send_text(msg_id, responses['term']['start'])
    elif step == 2:
        try:
            states[msg_id]['term'].append(pendulum.parse(text))
        except Exception as e:
            client.send_text(msg_id, responses['term']['invalid_date'])
            return
        update_state(msg_id, 'add.term#3')
        client.send_text(msg_id, responses['term']['end'])
    elif step == 3:
        try:
            states[msg_id]['term'].append(pendulum.parse(text))
        except Exception as e:
            client.send_text(msg_id, responses['term']['invalid_date'])
            return
        update_state(msg_id, '')
        user_id = db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0]
        lastrowid = db.execute('insert into Terms (userid, name, start, end) values(?,?,?,?)', (user_id, states[msg_id]['term'][0], states[msg_id]['term'][1], states[msg_id]['term'][2])).lastrowid
        db.commit()
        if lastrowid:
            update_state(msg_id, 'add.term#4')
            client.send_text(msg_id, responses['term']['success'])
            ask_affirmation(msg_id, responses['term']['post'])
        else:
            client.send_text(msg_id, responses['term']['error'])
            states[msg_id]['term'] = []
    elif step == 4:
        if 'affirmation' in message['message']['nlp']['entities']:
            print('Affirmed')
            if 'subject' in states[msg_id]:
                states[msg_id]['subject']['term'] = states[msg_id]['term'][0]
            else:
                states[msg_id]['subject'] = {'term': states[msg_id]['term'][0]}
            update_state(msg_id, 'add.subject#1')
            client.send_text(msg_id, responses['subject']['what'])
        else:
            states[msg_id]['term'] = []
            update_state(msg_id, '')
    
def add_subject(message, msg_id, text, status):
    def insert_subject(term):
        db.execute('insert into Subjects (userid, term_id, subject) values (?,?,?)', (db.execute('select user_id from Users where msg_id=?',(msg_id,)).fetchone()[0], db.execute('select id from Terms where name=?', (term,)).fetchone()[0], states[msg_id]['subject']['name']))
        db.commit()
        update_state(msg_id, 'add.subject#3')
        client.send_text(msg_id, responses['subject']['success'])
        ask_affirmation(msg_id, responses['subject']['post'])
        
    step = int(status.split('#')[1])
    if step == 1:
        if msg_id not in states:
            states[msg_id] = {}
        if 'subject' not in states[msg_id]:
            states[msg_id]['subject'] = {}
        states[msg_id]['subject']['name'] = text
        update_state(msg_id, 'add.subject#2')
        qr =  [QuickReply(y[0],y[0]) for y in db.execute('select Terms.name from Terms join Users on Users.user_id = Terms.userid where Users.msg_id = ?', (msg_id,)).fetchall()]
        if len(qr) == 0:
            update_state(msg_id, '')
            client.send_text(msg_id, responses['term']['no_term'])
        if 'term' in states[msg_id]['subject']:
            insert_subject(states[msg_id]['subject']['term'])
        else:
            client.send_quick_replies(msg_id, responses['subject']['term'], qr)
    if step == 2:
        insert_subject(text)
    if step == 3:
        if 'affirmation' in message['message']['nlp']['entities']:
            print('Affirmed')
            if 'class' not in states[msg_id]:
                states[msg_id]['class'] = {}
            states[msg_id]['class']['subject'] = states[msg_id]['subject']['name']
            ask_to_add_class(msg_id)
        states[msg_id]['subject'] = {}
            
            
def add_class(message, msg_id, text, status):
    step = int(status.split('#')[1])
    if step == 1:
        if 'affirmation' in message['message']['nlp']['entities']:
            user_id = db_users.get_user(msg_id=msg_id)['id']
            subject = db_subjects.get_subject(subject=states[msg_id]['class']['subject'])
            print(states)
            cursor = db.execute('insert into Classes'\
            '(userid, term_id, subject_id, module, start_time, end_time, repeat, location) '\
            'values (?,?,?,?,?,?,?,?)',\
            (user_id, subject['term_id'], subject['id'], states[msg_id]['class']['module'], states[msg_id]['class']['start_time'], states[msg_id]['class']['end_time'], states[msg_id]['class']['repeat'], states[msg_id]['class']['location']))
            db.commit()
            if cal.add_class(cursor.lastrowid):
                client.send_text(msg_id, responses['class']['success'])
            else:
                client.send_text(msg_id, responses['error']['general'])
            update_state(msg_id, '')
            
        else:
            update_state(msg_id, '')
            client.send_text(msg_id, responses['error']['not_Implemented'])

def ask_to_add_class(msg_id):
    qr =  [QuickReply(y[0],y[0]) for y in db.execute('select Subjects.subject from Subjects join Users on Users.user_id = Subjects.userid where Users.msg_id = ?', (msg_id,)).fetchall()]
    if len(qr) == 0:
        client.send_text(msg_id, responses['subject']['no_subject'])
        return
    client.send_buttons(msg_id, responses['class']['link'], [ActionButton(ButtonType.WEB_URL, responses['class']['add'], "https://winami.io/webviews/add_class", webview_height=WebviewType.TALL, messenger_extention=True)])
    update_state(msg_id, 'add.class#1')

def add_task(message, msg_id, text, status):
    step = int(status.split('#')[1])
    if step == 1:
        if 'affirmation' in message['message']['nlp']['entities']:
            user = db_users.get_user(msg_id=msg_id)
            if states[msg_id]['task']['subject'] != 'no_subject':
                subject = db_subjects.get_subject(subject=states[msg_id]['class']['subject'])['id']
            else:
                subject = None
            cursor = db.execute('insert into Tasks'\
            '(userid, subject_id, name, due, time_left) '\
            'values (?,?,?,?,?)',\
            (user['id'], subject, states[msg_id]['task']['name'],\
            pendulum.parse(states[msg_id]['task']['due_date'] + '  ' + states[msg_id]['task']['due_time'], user['timezone']),
            int(states[msg_id]['task']['time_left'])))
            db.commit()
            if cal.add_class(cursor.lastrowid):
                client.send_text(msg_id, responses['class']['success'])
            else:
                client.send_text(msg_id, responses['error']['general'])
            update_state(msg_id, '')
            
        else:
            update_state(msg_id, '')
            client.send_text(msg_id, responses['error']['not_Implemented'])

def ask_to_add_task(msg_id):
    client.send_buttons(msg_id, responses['task']['link'], [ActionButton(ButtonType.WEB_URL, responses['task']['add'], "https://winami.io/webviews/add_task", webview_height=WebviewType.TALL, messenger_extention=True)])
    update_state(msg_id, 'add.task#1')

def report_issue(message, msg_id, text, status):
    step = int(status.split('#')[1])
    if step == 0:
        url = 'https://api.github.com/repos/kartikye/sch/issues'
        session = requests.Session()
        session.auth = (config.github_username_bot, config.github_password_bot)
        
        issue = {
            'title': text[:20]+'...',
            'body': text,
            'labels': ['user_submitted_issue']
        }
        
        r = session.post(url, json.dumps(issue))
        if r.status_code == 201:
            client.send_text(msg_id, responses['report']['success'])
        else:
            client.send_text(msg_id, responses['report']['error'])
        update_state(msg_id, '')
        
def do_help(message, msg_id, text):
    client.send_text(msg_id, responses['help'])
    update_state(msg_id, '')

def do_report_issue(message, msg_id, text):
    update_state(msg_id, 'report.issue#0')
    client.send_text(msg_id, responses['report']['pre'])
    
def ask_affirmation(msg_id, question):
    client.send_quick_replies(msg_id, question, [QuickReply('Yes', 'Yes'), QuickReply('No', 'No')])
    
def update_state(msg_id, status):
    db.execute('update Conversation set status = ? where msg_id = ?', (status, msg_id))
    db.commit()