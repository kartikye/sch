from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from db import db_config, db_users, db_subjects
import json, pendulum
from msg_handlers import main_handler, responses #import states, update_state, ask_affirmation

responses = responses.responses

db = db_config.create_db_connection()

webview = Blueprint('webview', __name__, template_folder='templates')

@webview.route('/subjects/<msg_id>', methods=['GET'])
def subjects(msg_id):
    s = [y[0] for y in db.execute('select subject from Subjects join Users on Subjects.userid = Users.user_id where Users.msg_id = ?', (msg_id,)).fetchall()]    
    return json.dumps(s)

@webview.route('/add_class', methods=["GET", "POST"])
def add_class():
    if request.method == 'GET':
        return render_template('add_class.html')
    else:
        data = request.form
        msg_id = data['id']
        if msg_id not in main_handler.states:
            main_handler.states[msg_id] = {}
        if 'class' not in main_handler.states[msg_id]:
            main_handler.states[msg_id]['class'] = {}
        main_handler.states[msg_id]['class']['module'] = data['module']
        main_handler.states[msg_id]['class']['subject'] = data['subject']
        main_handler.states[msg_id]['class']['start_time'] = data['start_time']
        main_handler.states[msg_id]['class']['end_time'] = data['end_time']
        main_handler.states[msg_id]['class']['repeat'] = data['repeat']
        if 'location' in data:
            main_handler.states[msg_id]['class']['location'] = data['location']
        else:
            data['location'] = 'None'
        main_handler.update_state(msg_id, 'add.class#1')
        main_handler.ask_affirmation(msg_id, responses['class']['verify'].format(data['subject'], data['module'], pendulum.parse(data['start_time'], strict=True).format('h:mm A', formatter='alternative') , pendulum.parse(data['end_time'], strict=True).format('h:mm A', formatter='alternative') , data['repeat'], data['location']))
        return 'hi', 200
        
@webview.route('/add_task', methods=["GET", "POST"])
def add_task():
    if request.method == 'GET':
        return render_template('add_task.html')
    else:
        data = request.form
        print(data)
        msg_id = data['id']
        print(msg_id)
        if msg_id not in main_handler.states:
            main_handler.states[msg_id] = {}
        if 'task' not in main_handler.states[msg_id]:
            main_handler.states[msg_id]['task'] = {}
        print(1)
        main_handler.states[msg_id]['task']['name'] = data['name']
        print(2)
        main_handler.states[msg_id]['task']['subject'] = data['subject']
        print(3)
        main_handler.states[msg_id]['task']['due_date'] = data['due_date']
        print(4)
        main_handler.states[msg_id]['task']['due_time'] = data['due_time']
        print(5)
        main_handler.states[msg_id]['task']['time_left'] = data['time_left']
        print(6)
        main_handler.update_state(msg_id, 'add.task#1')
        print(7)
        try: 
            main_handler.ask_affirmation(msg_id, "hi");#responses['task']['verify'].format(data['name'], data['subject'], pendulum.parse(data['due_date'], strict=True).format('D MMM YYYY', formatter='alternative') , pendulum.parse(data['end_time'], strict=True).format('h:mm A', formatter='alternative') , data['time_left']))
        except Exception as e:
            print(e)
        return 'hi', 200