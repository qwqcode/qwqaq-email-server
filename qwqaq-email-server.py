# encoding: utf-8

import os
import smtplib
import json
import traceback
from flask import Flask, abort, request, jsonify
from flask_mail import Mail, Message
from threading import Thread
import time, datetime

app = Flask(__name__)

DATA_FILE = os.path.dirname(os.path.realpath(__file__)) + '/data.json'
CONF_FILE = os.path.dirname(os.path.realpath(__file__)) + '/conf.json'

conf = {
    'host': '0.0.0.0',
    'port': 51232,
    'password': '',
    'mail_server': 'smtp.qq.com',
    'mail_username': 'test@qq.com',
    'mail_password': '',
    'mail_port': 465,
    'mail_use_ssl': True,
    'mail_use_tls': False,
}

data = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    save_data()
    print(DATA_FILE + ' 已创建')

try:
    with open(CONF_FILE, 'r', encoding='utf-8') as json_file:
        conf.update(json.load(json_file))
except FileNotFoundError:
    with open(CONF_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(conf, json_file, ensure_ascii=False)
    print(DATA_FILE + ' 已创建')

# print(conf)

app.config['MAIL_DEBUG'] = False
app.config['MAIL_SUPPRESS_SEND'] = False # 是否发送邮件，True 则不发送
app.config['MAIL_SERVER'] = conf['mail_server']
app.config['MAIL_PORT'] = conf['mail_port']
app.config['MAIL_USE_SSL'] = conf['mail_use_ssl']
app.config['MAIL_USE_TLS'] = conf['mail_use_tls']
app.config['MAIL_USERNAME'] = conf['mail_username']
app.config['MAIL_PASSWORD'] = conf['mail_password']

mail = Mail(app)

def send_async_email(app, mail_id, mail_title, mail_content, mail_recipient):
    data[mail_id] = {
        'mail_id': mail_id, 'mail_title': mail_title, 'mail_content': mail_content, 'mail_recipient': mail_recipient
    }

    msg = Message(subject=mail_title, sender=("QWQAQ", "1149527164@qq.com"))
    msg.html = mail_content
    msg.add_recipient(mail_recipient)

    with app.app_context():
        data[mail_id]['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data[mail_id]['type'] = 'sending'
        print('['+str(mail_id)+'][状态: 发送中][标题: '+mail_title+'][To: '+mail_recipient+'][Date: '+data[mail_id]['created_at']+']')

        try:
            mail.send(msg)
        except smtplib.SMTPRecipientsRefused:
            data[mail_id]['error'] = "Unable to send email to"
        except smtplib.SMTPAuthenticationError:
            data[mail_id]['error'] = "Authentication error when sending Email"
        except Exception as e:
            data[mail_id]['error'] = traceback.format_exc()
        
        data[mail_id]['done_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data[mail_id]['type'] = 'success' if 'error' not in data[mail_id] else 'error'
        print('['+str(mail_id)+'][状态: '+data[mail_id]['type']+'][标题: '+mail_title+'][To: '+mail_recipient+'][Date: '+data[mail_id]['done_at']+']')
        save_data()

@app.route('/')
def index():
    if request.args.get('password') != conf['password']:
        return jsonify({'success': False, 'msg': '密码错误'})
    
    mail_content = request.args.get('mail_content')
    mail_title = request.args.get('mail_title')
    mail_recipient = request.args.get('mail_recipient')

    if mail_title is None:
        return jsonify({'success': False, 'msg': 'mail_title 不能为空'})
    if mail_content is None:
        return jsonify({'success': False, 'msg': 'mail_content 不能为空'})
    if mail_recipient is None:
        return jsonify({'success': False, 'msg': 'mail_recipient 不能为空'})

    mail_id = len(data)+1
    thread = Thread(target=send_async_email, args=[app, mail_id, mail_title, mail_content, mail_recipient])
    thread.start()

    return jsonify({'success': True, 'msg': '已开始执行异步邮件发送任务'})

if __name__ == '__main__':
    # app.run(debug=True)
    print('*** QWQAQ EMAIL SERVER RUNNING ***')
    app.run(host=conf['host'], port=conf['port'])