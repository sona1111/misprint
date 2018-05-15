from app import app, mail
import pymongo
from flask_mail import Message
from flask import url_for
from threading import Thread
from functions import get_db_proc

def send_async_email(msg):
    with app.app_context():
        mail.send(msg)





database = get_db_proc()
coll = database.emails

TICKET_EMAIL_TEMPLATE = """
<html lang='en'>
<body>
<h3>The following ticket has been opened automatically following a support chat request.</h3>

<h4>User Information</h4>
<table border = '1'>
    <tr><td>User ID</td><td>{userid}</td></tr>
    <tr><td>User Name</td><td>{fname} {lname}</td></tr>
    <tr><td>Room</td><td>{room}</td></tr>
</table>

<h4>Chat log</h4>
<table border = '4'>
    {chat_log}
</table>
</body></html>
"""


def send_create_ticket_email(user, fname, lname, msgs, room=None):
    subject = "CLASSROOM EMERGENCY: %s %s (%s)" % (fname, lname, user)
    if room:
        subject += " in room '%s'" % room
    sender = app.config['MAIL_SENDER']

    chatTable = ""
    chatRow = "<tr><td>{fname} {lname}</td><td>{msg}</td></tr>"
    for msg in msgs:
        if not 'joined' in msg and not 'left' in msg:
            chatTable += chatRow.format(fname=msg['fname'],
                                        lname=msg['lname'],
                                        msg=msg['msg'])

    body = TICKET_EMAIL_TEMPLATE.format(userid=user,
                                        fname=fname,
                                        lname=lname,
                                        room=room.split('-')[0] if len(room.split('-')) > 1 else 'Unknown',
                                        chat_log=chatTable)

    mail_to_be_sent = Message(subject=subject, sender=sender, recipients=app.config['TICKET_CREATION_EMAILS'])
    mail_to_be_sent.html = body

    thr = Thread(target=send_async_email, args=[mail_to_be_sent])
    thr.start()

def send_awaiting_confirm_mail_admin(user):
    mailCfg = coll.find_one({'_id':'send_awaiting_confirm_mail_admin'}, {"_id":0})
    """
    Send the awaiting for confirmation mail to the administrator for approval.
    """
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=app.config['ACCOUNT_APPROVAL_EMAILS'])
    confirmation_url = 'http://sonic.mashframe.com/activate_user_admin/' + user['userHashAdmin']
    mail_to_be_sent.html = mailCfg['body'] % (user['_id'], user['email'], user['firstName'], user['lastName'], user['company'], user['officePhone'], user['mobilePhone'], user['street'], user['city'], user['state'], user['zip'], user['country'], confirmation_url)

    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    

def send_awaiting_confirm_mail(user):
    mailCfg = coll.find_one({'_id':'send_awaiting_confirm_mail'}, {"_id":0})
    """
    Send the awaiting for confirmation mail to the user.
    """
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=[user['email']])
    confirmation_url = '%sactivate_user_client/%s' % (url_for('index', _external=True), user['userHash'])
    mail_to_be_sent.body = mailCfg['body'] % (user['firstName'], confirmation_url)
    
    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    
def send_user_activated_mail(user):
    mailCfg = coll.find_one({'_id':'send_user_activated_mail'}, {"_id":0})
    """
    Send the awaiting for confirmation mail to the user.
    """
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=[user['email']])    
    mail_to_be_sent.body = mailCfg['body'] % (user['firstName'])
    
    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    
    
def send_forgot_username_mail(user):
    mailCfg = coll.find_one({'_id':'send_forgot_username_mail'}, {"_id":0})
    """
    Send the username reminder email
    """
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=[user['email']])
    username = user['_id']
    mail_to_be_sent.body = mailCfg['body'] % (username)
    
    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    
    
def send_forgot_password_mail(user):
    mailCfg = coll.find_one({'_id':'send_forgot_password_mail'}, {"_id":0})
    """
    Send the username reminder email
    """
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=[user['email']])
    password = user['password']
    mail_to_be_sent.body = mailCfg['body'] % (password)
    
    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    
    
def send_error_to_webmaster(tb):
    mailCfg = coll.find_one({'_id':'send_error_to_webmaster'}, {"_id":0})
    
    subject = mailCfg['subject']
    sender = mailCfg['sender']
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=app.config['WEBMASTER_EMAIL_ADDRESSES'])    
    mail_to_be_sent.body = mailCfg['body'] % (tb)
    
    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()

def send_test_mail(address):


    subject = "test message"
    sender = "Rudraya Support <support@rudraya.com>"
    mail_to_be_sent = Message(subject=subject, sender = sender, recipients=[address])
    mail_to_be_sent.body = "a test body"

    thr = Thread(target = send_async_email, args = [mail_to_be_sent])
    thr.start()
    
