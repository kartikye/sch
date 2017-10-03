import config
from db import db_config
from db import db_users
#from calendar import cal
from flask import Flask, render_template, request
from pymessager.message import Messager
client = Messager(config.facebook_access_token)
import os
import json

from msg_handlers import main_handler, notification_handler, responses
import traceback
from webviews.webviews import webview

responses = responses.responses


app = Flask(__name__, static_url_path="/static", static_folder="webviews/static")


app.register_blueprint(webview, url_prefix='/webviews')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/msg/webhook', methods=["GET"])
def fb_webhook():
    verification_code = 'I_AM_VERIFICIATION_CODE'
    verify_token = request.args.get('hub.verify_token')
    if verification_code == verify_token:
        return request.args.get('hub.challenge')

@app.route('/msg/webhook', methods=['POST'])
def fb_receive_message():
    message_entries = json.loads(request.data.decode('utf8'))['entry']
    print(message_entries)
    for entry in message_entries:
        for message in entry['messaging']:
            if message.get('message') and 'attachments' not in message['message']:
                try:
                    main_handler.handle(message)
                    print("{sender[id]} says {message[text]}".format(**message))
                except Exception as e:
                    print('--------------ERROR----------------')
                    print(e)
                    print('-----------------------------------')
                    traceback.print_exc()
                    print('-----------------------------------')
                    client.send_text('1628181117202388', ['Hi boss, \nAn error occured when a user sent the following message:', message['message']['text'], 'Here is the error:','```C\n'+traceback.format_exc()+'\n```'])
                    client.send_text(message['sender']['id'], responses['error']['general'])
                    main_handler.update_state(message['sender']['id'], '')

    return "Hi", 200


@app.route('/send_notifications')
def send_notifications():
    notification_handler.handle()
    return 'hi', 200
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 443))
    app.run(host="0.0.0.0", port=port, ssl_context=('cert.pem', 'key.pem'))