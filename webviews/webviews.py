from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from db import db_config
import json

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
        print("-------------------------------------------")
        print(request.form)
        return 'hi', 200