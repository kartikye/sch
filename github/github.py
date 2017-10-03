import requests, json
import config

url = 'https://api.github.com/repos/kartikye/sch/issues'
session = requests.Session()
session.auth = (config.github_username_bot, config.github_password_bot)

def insert_issue(body, label):

    issue = {
        'title': body[:20]+'...',
        'body': body,
        'labels': [label]
    }

    r = session.post(url, json.dumps(issue))

    if r.status_code == 201:
        return True
    else:
        return False
        