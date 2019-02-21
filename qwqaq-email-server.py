# encoding: utf-8

import os
import smtplib
import json
import traceback
import time, datetime
from flask import Flask, abort, request, jsonify
from flask_mail import Mail, Message
from threading import Thread

_app = Flask(__name__)
_conf = {
    'host': '0.0.0.0',
    'port': 51232,
    'password': '',
    'mail_server': 'smtp.qq.com',
    'mail_username': 'test@qq.com',
    'mail_password': '',
    'mail_sender_name': '',
    'mail_sender_addr': '',
    'mail_port': 465,
    'mail_use_ssl': True,
    'mail_use_tls': False,
}
_data = {}

CONF_FILE = os.path.dirname(os.path.realpath(__file__)) + '/conf.json'
DATA_FILE = os.path.dirname(os.path.realpath(__file__)) + '/data.json'

try:
    with open(CONF_FILE, 'r', encoding='utf-8') as json_file:
        _conf.update(json.load(json_file))
except FileNotFoundError:
    with open(CONF_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(_conf, json_file, ensure_ascii=False)
    print('[配置文件] '+CONF_FILE+' 已创建')

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(_data, json_file, ensure_ascii=False)

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as json_file:
        _data = json.load(json_file)
except FileNotFoundError:
    save_data()
    print('[数据文件] '+DATA_FILE+' 已创建')

_app.config['MAIL_DEBUG'] = False
_app.config['MAIL_SUPPRESS_SEND'] = False # 是否发送邮件，True 则不发送
_app.config['MAIL_SERVER'] = _conf['mail_server']
_app.config['MAIL_PORT'] = _conf['mail_port']
_app.config['MAIL_USE_SSL'] = _conf['mail_use_ssl']
_app.config['MAIL_USE_TLS'] = _conf['mail_use_tls']
_app.config['MAIL_USERNAME'] = _conf['mail_username']
_app.config['MAIL_PASSWORD'] = _conf['mail_password']

_mail = Mail(_app)

def send_async_email(mail_id, mail_title, mail_content, mail_recipient):
    _data[mail_id] = {
        'mail_id': mail_id, 'mail_title': mail_title, 'mail_content': mail_content, 'mail_recipient': mail_recipient
    }

    msg = Message(subject=mail_title, sender=(_conf['mail_sender_name'], _conf['mail_sender_addr']))
    msg.html = mail_content
    msg.add_recipient(mail_recipient)

    with _app.app_context():
        _data[mail_id]['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        _data[mail_id]['type'] = 'sending'
        print('['+str(mail_id)+'][状态: 发送中][标题: '+mail_title+'][To: '+mail_recipient+'][Date: '+_data[mail_id]['created_at']+']')

        try:
            _mail.send(msg)
        except smtplib.SMTPRecipientsRefused:
            _data[mail_id]['error'] = "Unable to send email to"
        except smtplib.SMTPAuthenticationError:
            _data[mail_id]['error'] = "Authentication error when sending Email"
        except Exception as e:
            _data[mail_id]['error'] = traceback.format_exc()
        
        _data[mail_id]['done_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        _data[mail_id]['type'] = 'success' if 'error' not in _data[mail_id] else 'error'
        print('['+str(mail_id)+'][状态: '+_data[mail_id]['type']+'][标题: '+mail_title+'][To: '+mail_recipient+'][Date: '+_data[mail_id]['done_at']+']')
        save_data()

@_app.route('/')
def index():
    if request.args.get('password') != _conf['password']:
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

    mail_id = len(_data)+1
    thread = Thread(target=send_async_email, args=[mail_id, mail_title, mail_content, mail_recipient])
    thread.start()

    return jsonify({'success': True, 'msg': '已开始执行异步邮件发送任务'})

if __name__ == '__main__':
    # app.run(debug=True)
    print('*** QWQAQ EMAIL SERVER RUNNING ***')
    _app.run(host=_conf['host'], port=_conf['port'])