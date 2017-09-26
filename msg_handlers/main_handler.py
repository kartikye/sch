from run import client
from pymessager.message import QuickReply
from db import db_config, db_users
import requests, json, config
import pendulum
db = db_config.create_db_connection()

states = {}

def loud_print(s):
    print('###############################################')
    print(s)
    print('###############################################')

def handle(message):
    msg_id = message['sender']['id']
    text = message['message']['text']
    
    if  db.execute('select * from Users where msg_id = ?', (msg_id,)).fetchone() is None:
        data = json.loads(requests.get('https://graph.facebook.com/v2.6/'+msg_id+'?fields=first_name,last_name&access_token='+config.facebook_access_token).text)
        db_users.insert_user(data['first_name'], data['last_name'], msg_id, '')
        update_state(msg_id, 'email#0')
        client.send_text(msg_id, "Hi " + data['first_name'] + ', thank you for using Schej! Schej will help you schedule you life and classes! Please enter your email so that we can send you a calendar.')
    
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
        'email': add_email,
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
        qr =  [QuickReply(y[0],y[0]) for y in db.execute('select Subjects.subject from Subjects join Users on Users.user_id = Subjects.userid where Users.msg_id = ?', (msg_id,)).fetchall()]
        if len(qr) == 0:
            client.send_text(msg_id, 'No subjects found. Please add a subject to add a class.')
            return
        update_state(msg_id, 'add.class#1')
        client.send_quick_replies(msg_id, 'What is the subject?', qr)
    elif item == 'homework':
        pass
    elif item == 'activity':
        pass
    elif item == 'meeting':
        pass
    else:
        pass
def add_email(message, msg_id, text, status):
    message = message['message']
    db.execute('update Users set email = ? where msg_id = ?', (message['text'], msg_id))
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
            print('---------------------------------------------------')
            print(e)
            client.send_text(msg_id, 'That is an invalid date, please try again')
            return
        update_state(msg_id, 'add.term#3')
        client.send_text(msg_id, 'When does the term end?')
    elif step == 3:
        try:
            states[msg_id]['term'].append(pendulum.parse(text))
        except Exception as e:
            print(e)
            client.send_text(msg_id, 'That is an invalid date, please try again')
            return
        update_state(msg_id, '')
        user_id = db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0]
        lastrowid = db.execute('insert into Terms (userid, name, start, end) values(?,?,?,?)', (user_id, states[msg_id]['term'][0], states[msg_id]['term'][1], states[msg_id]['term'][2])).lastrowid
        db.commit()
        if lastrowid:
            client.send_text(msg_id, 'Term added')
            update_state(msg_id, 'add.term#4')
            ask_affirmation(msg_id, 'Do you want to add a subject?')
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
        states[msg_id]['term'] = []
    
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
            update_state(msg_id, 'add.class#2')
            client.send_text(msg_id, "What module?")
        states[msg_id]['subject'] = {}
            
            
def add_class(message, msg_id, text, status):
    step = int(status.split('#')[1])
    if step == 1:
        if msg_id not in states:
            states[msg_id] = {}
        if 'class' not in states[msg_id]:
            states[msg_id]['class'] = {}
        states[msg_id]['class']['subject'] = text
        update_state(msg_id, 'add.class#2')
        client.send_text(msg_id, 'What module?')
    if step == 2:
        states[msg_id]['class']['module'] = text
        update_state(msg_id, 'add.class#3')
        client.send_text(msg_id, 'What time does the class start? (HH:MM)')
    if step == 3:
        states[msg_id]['class']['start'] = text
        update_state(msg_id, 'add.class#4')
        client.send_text(msg_id, 'What time does the class end? (HH:MM)')
    if step == 4:
        states[msg_id]['class']['end'] = text
        update_state(msg_id, 'add.class#5')
        client.send_text(msg_id, 'What days does the class repeat? (m t w th f s su) Please seperate days with a space.')
    if step == 5:
        for d in text.split(' '):
            if d not in ['m', 't', 'w', 'th', 'f', 's', 'ss']:
                client.send_text(msg_id, 'Sorry, that is not a valid input. Please try again')
                return
        states[msg_id]['class']['days'] = text
        update_state(msg_id, 'add.class#6')
        client.send_text(msg_id, 'What is the class location?')
    if step == 6:
        db.execute('insert into Classes (userid, term_id, subject_id, start_time, end_time, repeat, location')
        
def add_email(message, msg_id, text, status):
    message = message['message']
    db.execute('update Users set email = ? where msg_id = ?', (message['text'], msg_id))
    db.commit()
    cal.create_calendar(db.execute('select user_id from Users where msg_id = ?', (msg_id,)).fetchone()[0])
    client.send_text(msg_id, 'Your calendar has been created. Please check your email for the invite.')
    update_state(msg_id, 'add.term#1')
    client.send_text(msg_id, "To get started, lets add a term. What is the term name?")
    
def do_help(message, msg_id, text):
    client.send_text(msg_id, 'Here are the commands you can use:')
    client.send_text(msg_id, "To add an item, say 'add <item>'. You can add a term, subject, class, homework, exam, activity and meeting")
    update_state(msg_id, '')
    
def ask_affirmation(msg_id, question):
    client.send_quick_replies(msg_id, question, [QuickReply('Yes', 'Yes'), QuickReply('No', 'No')])
    
def update_state(msg_id, status):
    db.execute('update Conversation set status = ? where msg_id = ?', (status, msg_id))
    db.commit()