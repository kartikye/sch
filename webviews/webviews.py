from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from db import db_config, db_users, db_subjects
import json
from msg_handlers import main_handler #import states, update_state, ask_affirmation

db = db_config.create_db_connection()

webview = Blueprint('webview', __name__, template_folder='templates')

@webview.route('/subjects/<msg_id>', methods=['GET'])
def subjects(msg_id):
    s = [y[0] for y in db.execute('select subject from Subjects join Users on Subjects.userid = Users.user_id where Users.msg_id = ?', (msg_id,)).fetchall()]    
    return json.dumps(s)

@webview.route('/add_class', methods=["GET", "POST"])
def show():
    if request.method == 'GET':
        return render_template('add_class.html')
    else:
        data = request.form
        print(data)
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
        main_handler.update_state(msg_id, 'add.class#1')
        main_handler.ask_affirmation(msg_id, 'Is this ok?')
        return 'hi', 200