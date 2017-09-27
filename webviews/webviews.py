from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound

webview = Blueprint('webview', __name__, template_folder='templates')

@webview.route('/add_class', methods=["GET", "POST"])
def show():
    if request.method == 'GET':
        return render_template('add_class.html')
    else:
        print("-------------------------------------------")
        print(request.form)
        return 'hi', 200