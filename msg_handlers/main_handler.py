from run import client
from pymessager.message import QuickReply, ActionButton, WebviewType, ButtonType
from db import *
import requests, json, config
import pendulum
db = db_config.create_db_connection()
from cal import cal
import re

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
        client.send_text(msg_id, "Hi " + data['first_name'] + ', thank you for using Schej! Schej will help you schedule you life and classes! Please enter your email so that we can send you a calendar.')
        return
    
    status = db.execute('select status from Conversation where msg_id = ?', (msg_id,)).fetchone()[0]
    
    #Check for mistake 

    if 'mistake' in message['message']['nlp']['entities'] and message['message']['nlp']['entities']['mistake'][0]['confidence'] > .9:
        if message['message']['nlp']['entities']['mistake'][0]['value'] == 'fuck':
            client.send_text(msg_id, 'Do you talk to your mother with that mouth??')
        client.send_text(msg_id, 'No problem, try again!')
        return
    if 'exit' in message['message']['nlp']['entities'] and message['message']['nlp']['entities']['exit'][0]['confidence'] > .9:
        client.send_text(msg_id, 'Cancelling action')
        update_state(msg_id, '')
        return

    switch = {
        '' : no_status,
        'setup': setup,
        'add.term': add_term,
        'add.subject': add_subject,
        'add.class': add_class
    }
    
    switch[status.split('#')[0]](message, msg_id, text, status)
    
def no_status(message, msg_id, text, status):
    message = message['message']
    print(message['nlp']['entities'])
    
    if 'action' in message['nlp']['entities']:
        if message['nlp']['entities']['action'][0]['value'] == 'add':
            do_add(message, msg_id, text)
    elif 'help' in message['nlp']['entities']:
        do_help(message, msg_id, text)
        
def do_add(message, msg_id, text):
    print('do_add')
    
    item =  message['nlp']['entities']['item'][0]['value']
    if item == 'term':
        update_state(msg_id, 'add.term#1')
        client.send_text(msg_id, "What is the term name?")
    elif item == 'subject':
        if len(db.execute('select Terms.name from Terms join Users on Users.user_id = Terms.userid where Users.msg_id = ?', (msg_id,)).fetchall()) == 0:
            client.send_text(msg_id, 'There are no terms, please add a term first.')
            return
        update_state(msg_id, 'add.subject#1')
        client.send_text(msg_id, "What is the subject?")
    elif item == 'class':
        ask_to_add_class(msg_id)
    elif item == 'homework':
        pass
    elif item == 'activity':
        pass
    elif item == 'meeting':
        pass
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
            client.send_text(msg_id, ':(')
            client.send_text(msg_id, text + ' does not seem like a valid email. Please try again.')
    if step == 1:
        if 'affirmation' in message['nlp']['entities']:
            db.execute('update Users set email = ? where msg_id = ?', (states[msg_id]['setup']['email'], msg_id))
            db.commit()
            update_state(msg_id, 'setup#2')
            client.send_text(msg_id, 'Which city so you live in? (We need to find your timezone for your calendar)')
        else:
            update_state(msg_id, 'setup#0')
            client.send_text(msg_id, ':(')
            client.send_text(msg_id, 'Please enter your email again!')
    if step == 2:
        try:
            coordinates = json.loads(requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+text+',+CA&sensor=false').text)['results'][0]['geometry']['location']
            timezone = json.loads(requests.get('https://maps.googleapis.com/maps/api/timezone/json?location='+str(coordinates['lat'])+','+str(coordinates['lng'])+'&timestamp='+str(pendulum.now().int_timestamp)+'&sensor=false').text)['timeZoneId']
        except Exception as e:
            print(e)
            client.send_text(msg_id,"Sorry, we couldn't find that timezone. Please try again.")
            return
        db.execute('update Users set timezone = ? where msg_id = ?', (timezone, msg_id))
        db.commit()
        cal.create_calendar(db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0])
        client.send_text(msg_id, 'Your calendar has been created. Please check your email for the invite.')
        update_state(msg_id, 'add.term#1')
        client.send_text(msg_id, "To get started, lets add a term. What is the term name?")
            
            
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
        client.send_text(msg_id, 'When does the term start?')
    elif step == 2:
        try:
            states[msg_id]['term'].append(pendulum.parse(text))
        except Exception as e:
            client.send_text(msg_id, 'That is an invalid date, please try again')
            return
        update_state(msg_id, 'add.term#3')
        client.send_text(msg_id, 'When does the term end?')
    elif step == 3:
        try:
            states[msg_id]['term'].append(pendulum.parse(text))
        except Exception as e:
            client.send_text(msg_id, 'That is an invalid date, please try again')
            return
        update_state(msg_id, '')
        user_id = db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0]
        lastrowid = db.execute('insert into Terms (userid, name, start, end) values(?,?,?,?)', (user_id, states[msg_id]['term'][0], states[msg_id]['term'][1], states[msg_id]['term'][2])).lastrowid
        db.commit()
        if lastrowid:
            client.send_text(msg_id, 'Term added')
            update_state(msg_id, 'add.term#4')
            ask_affirmation(msg_id,'Do you want to add a subject?')
        else:
            client.send_text(msg_id, 'Term could not be added')
            states[msg_id]['term'] = []
    elif step == 4:
        if 'affirmation' in message['message']['nlp']['entities']:
            print('Affirmed')
            if 'subject' in states[msg_id]:
                states[msg_id]['subject']['term'] = states[msg_id]['term'][0]
            else:
                states[msg_id]['subject'] = {'term': states[msg_id]['term'][0]}
            update_state(msg_id, 'add.subject#1')
            client.send_text(msg_id, 'What is the subject?')
        else:
            states[msg_id]['term'] = []
            update_state(msg_id, '')
    
def add_subject(message, msg_id, text, status):
    def insert_subject(term):
        db.execute('insert into Subjects (userid, term_id, subject) values (?,?,?)', (db.execute('select user_id from Users where msg_id=?',(msg_id,)).fetchone()[0], db.execute('select id from Terms where name=?', (term,)).fetchone()[0], states[msg_id]['subject']['name']))
        db.commit()
        update_state(msg_id, 'add.subject#3')
        client.send_text(msg_id, 'Subject Added')
        ask_affirmation(msg_id, 'Do you want to add a class?')
        
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
            client.send_text(msg_id, 'There are no terms, please add a term first.')
        if 'term' in states[msg_id]['subject']:
            insert_subject(states[msg_id]['subject']['term'])
        else:
            client.send_quick_replies(msg_id, 'What term is the subject in?', qr)
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
            if cal.add_class(cursor.lastrowid)
                client.send_text(msg_id, 'Class added!')
            else:
                client.send_text(msg_id, 'Oops! Something went wrong')
            update_state(msg_id, '')
            
        else:
            update_state(msg_id, '')
            client.send_text(msg_id, 'Option to update coming soon!')

def ask_to_add_class(msg_id):
    qr =  [QuickReply(y[0],y[0]) for y in db.execute('select Subjects.subject from Subjects join Users on Users.user_id = Subjects.userid where Users.msg_id = ?', (msg_id,)).fetchall()]
    if len(qr) == 0:
        client.send_text(msg_id, 'No subjects found. Please add a subject to add a class.')
        return
    client.send_buttons(msg_id, 'Please create the class by clicking the link', [ActionButton(ButtonType.WEB_URL, "Add class", "https://winami.io/webviews/add_class", webview_height=WebviewType.TALL, messenger_extention=True)])
    update_state(msg_id, 'add.class#1')
        
def do_help(message, msg_id, text):
    client.send_text(msg_id, 'Here are the commands you can use:')
    client.send_text(msg_id, "To add an item, say 'add <item>'. You can add a term, subject, class, homework, exam, activity and meeting")
    update_state(msg_id, '')
    
def ask_affirmation(msg_id, question):
    client.send_quick_replies(msg_id, question, [QuickReply('Yes', 'Yes'), QuickReply('No', 'No')])
    
def update_state(msg_id, status):
    db.execute('update Conversation set status = ? where msg_id = ?', (status, msg_id))
    db.commit()