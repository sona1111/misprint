from app import app, socketio
from flask import Blueprint, render_template, request, abort, jsonify, session
from flask.ext.socketio import emit, join_room
from decorators import requireLoginLevel
import logging
from functions import get_db
from RvccApi.Core import getClassRecords, updateTerm
from PrinterApi.Core import getPrinterRecords
from datetime import timedelta
from bson import json_util
import json
import mailing
import random, string
from taskQueue import checkPrinters

logr = logging.getLogger(__name__)
MISPrint_B = Blueprint('MISPrint', __name__)


@socketio.on('connect', namespace='/MISPrint')
def connect():
    # join_room(session['user'])
    emit('connectConfirm', {'ok': 1, 'session':session['user']})



@MISPrint_B.route('/redirectOutput', methods = ['POST'])
def redirectOutput():


    if 'sessionID' in request.json and 'data' in request.json:
        #logr.info('received emit: %s' % request.json['sessionID'])
        payload = {'ok': 1, 'data':request.json['data']}
        if 'type' in request.json:
            payload['type'] = request.json['type']
        socketio.emit('printerUpdate', json.dumps(payload, default=json_util.default), room=request.json['sessionID'],
                      namespace='/MISPrint')

        return jsonify({'ok':1})
    elif 'data' in request.json:
        cr = getClassRecords()
        payload = {'ok': 1, 'data':request.json['data']}

        for i, printer in enumerate(payload['data']):
            timeUntilRoomOpen = [x for x in cr.getClassesNow(printer['room'])]
            if timeUntilRoomOpen and 'end' in timeUntilRoomOpen[0]:
                if 'end' in timeUntilRoomOpen[0]:
                    payload['data'][i]['roomOpen'] = (timeUntilRoomOpen[0]['end']).strftime("%a, %d %b %Y %H:%M:%S GMT")
                else:
                    payload['data'][i]['roomOpen'] = ''
            else:
                payload['data'][i]['roomOpen'] = ''

        if 'type' in request.json:
            payload['type'] = request.json['type']

        socketio.emit('printerUpdate', payload, broadcast=True, namespace='/MISPrint')
        return jsonify({'ok':1})

    else:
        return jsonify({'ok':0})


@MISPrint_B.route('/mainapp', methods = ['GET'])
@requireLoginLevel(2)
def mainapp():
    return render_template('mainapp.html')

@MISPrint_B.route('/helpchat', methods = ['GET'])
@requireLoginLevel(2)
def helpchat():

    return render_template('helpchat.html')

@MISPrint_B.route('/helpchatclient', methods = ['GET'])
@requireLoginLevel(2)
def helpchatclient():
    room=request.args['room'] if 'room' in request.args else None
    return render_template('helpchatclient.html', roomName=room, navEnabled=False)


@MISPrint_B.route('/getlocalmsgs', methods=['POST'])
def getlocalmsgs():
    #'natural' is a built in mongo to get the insertion order

    db = get_db()
    cur = [msg for msg in db.msgs.find({'room':'LOCAL', 'msg':{'$exists':True}},{'_id':0}).sort([('$natural',-1)]).limit(20)]
    #python slice syntax for [::-1] is to reverse the send order.
    return jsonify({'msgs':cur[::-1]})

@socketio.on('connect', namespace='/MISChat')
def connect2():
    # join_room(session['user'])
    room = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    emit('connectConfirm', {'ok': 1, 'room':room})

# @socketio.on('disconnect', namespace='/MISChat')
# def disconnect():
#     # join_room(session['user'])
#     emit('userDisconnect', {'ok': 1, 'user':session['user']}, broadcast=True)
@socketio.on('userDisconnect', namespace='/MISChat')
def userDisconnect(user, room, fname, lname, tStamp):
    db = get_db()
    db.msgs.insert({'room':room, 'user':user, 'fname':fname, 'lname':lname, 'left':True, 'time':tStamp})
    emit('userDisconnect', {'ok': 1, 'user':user, 'room':room,  'fname':fname, 'lname':lname, 'time':tStamp}, broadcast=True)
    if room != 'LOCAL':
        msgs = [msg for msg in db.msgs.find({'room': room, 'msg': {'$exists': True}}, {'_id': 0}).sort([('$natural', 1)])]
        print msgs
        if msgs:
            mailing.send_create_ticket_email(user, fname, lname, msgs, room)

@socketio.on('joined', namespace='/MISChat')
def joined(user, mode, room, fname, lname, tStamp):
    #at some point, twisted will be implemented instead of this
    #loggedIn.addUser(user)
    #print loggedIn.getUsers()
    db = get_db()
    db.msgs.insert({'room':room, 'user':user, 'fname':fname, 'lname':lname, 'joined':True, 'time':tStamp})
    emit('joined', {'user':user,'mode':mode, 'room':room, 'fname':fname, 'lname':lname, 'time':tStamp}, broadcast=True)

@socketio.on('changedStatus', namespace='/MISChat')
def changedStatus(user, status):
    emit('changedStatus', {'user':user, 'status':status}, broadcast=True)

@socketio.on('checkUsersOnlineInit', namespace='/MISChat')
def checkUsersOnlineInit():
    emit('checkUsersOnlineInit', {}, broadcast=True)

@socketio.on('checkUsersOnlineConfirm', namespace='/MISChat')
def checkUsersOnlineConfirm(user, mode, status, fname, lname, tStamp):
    if mode == 'client':
        db = get_db()
        cur = [msg for msg in db.msgs.find({'room':status, 'msg':{'$exists':True}},{'_id':0}).sort([('$natural',-1)]).limit(20)]
        emit('checkUsersOnlineConfirm', {'msgs':cur, 'user':user, 'mode':mode, 'room':status, 'fname':fname, 'lname':lname, 'time':tStamp}, broadcast=True)
    elif mode == 'staff':
        emit('checkUsersOnlineConfirm', {'user':user, 'mode':mode, 'status':status, 'fname':fname, 'lname':lname, 'time':tStamp}, broadcast=True)

@socketio.on('chatMsg', namespace='/MISChat')
def chatMsg(user, fname, lname, data, room, tStamp):
    #
    # #msgs.insert({'post':message})
    # if message != 'connected':
    #
    #     msgsCol.insert({'user':message['user'], 'msg':message['post']})
    #
    #     emit('update', message, broadcast=True)
    db = get_db()
    db.msgs.insert({'room':room, 'user':user, 'fname':fname, 'lname':lname, 'msg':data, 'time':tStamp})
    emit('chatMsg', {'user':user,  'fname':fname, 'lname':lname, 'data':data, 'room':room, 'time':tStamp}, broadcast=True)

@socketio.on('crazyrotate')
def crazyrotate():
    emit('crazyrotate', broadcast=True)


#used to send any data before disconnect
@socketio.on('preDisconnect')
def preDisconnect(user):
    pass
    #userLeft(user)

# 'disconnected' is a special event
@socketio.on('disconnect')
def disconnected():
    pass

@MISPrint_B.route('/refreshPrintersNow', methods = ['GET', 'POST'])
@requireLoginLevel(2)
def refreshPrintersNow():
    checkPrinters.delay()
    return jsonify({'ok':1})

@MISPrint_B.route('/getImportantPrinterData', methods = ['POST'])
@requireLoginLevel(2)
def getImportantPrinterData():

    pr = getPrinterRecords()
    data = pr.getAllImportant()
    cr = getClassRecords()
    for i, printer in enumerate(data):
        timeUntilRoomOpen = [x for x in cr.getClassesNow(printer['room'])]

        if timeUntilRoomOpen:
            data[i]['roomOpen'] = timeUntilRoomOpen[0]['end']
        else:
            data[i]['roomOpen'] = ''
    return jsonify({'printers':data})

@MISPrint_B.route('/getPrinterData', methods = ['POST'])
@requireLoginLevel(2)
def getPrinterData():

    pr = getPrinterRecords()
    if 'room' in request.json:
        data = pr.getAllPrinterStatus(room=request.json['room'])
    else:
        data = pr.getAllPrinterStatus()

    out = [x for x in data]
    return jsonify({'printers':out})


@MISPrint_B.route('/getClassData', methods = ['POST'])
@requireLoginLevel(2)
def getClassData():

    cr = getClassRecords()
    if 'start' in request.json:
        if not request.json['start'] or not request.json['end']:
            return jsonify({'classes':[]})
        data = cr.getClassesRange(request.json['start'],
                                  request.json['end'],
                                  request.json.get('room', None))
        out = {'classes': [x for x in data]}
    else:
        data = cr.getClassesNow(request.json.get('room', None))


        out = {'classes':[x for x in data]}
        data = cr.getClassesBeginning(request.json.get('room', None))
        out['classesBeginning'] = [x for x in data]

    return jsonify(out)

@MISPrint_B.route('/getAllClassRooms', methods = ['POST'])
@requireLoginLevel(2)
def getAllClassRooms():

    cr = getClassRecords()
    out = sorted([x for x in cr.getAllRoomNames()])

    return jsonify({'rooms':out})

@MISPrint_B.route('/getAllPrinterRooms', methods = ['POST'])
@requireLoginLevel(2)
def getAllPrinterRooms():

    pr = getPrinterRecords()
    out = sorted([x for x in pr.getAllRoomNames()])

    return jsonify({'rooms':out})

@MISPrint_B.route('/admin', methods = ['GET'])
@requireLoginLevel(1)
def admin():
    return render_template("admin.html")

@MISPrint_B.route('/updateTermRun', methods = ['POST'])
@requireLoginLevel(1)
def updateTermRun():
    if not 'term' in request.json:
        return jsonify({'ok':0, 'err':'must provide term to update term'})
    try:
        updateTerm(request.json['term'])
    except Exception, e:
        return jsonify({'ok':0, 'err':'ERROR: %s' % str(e)})
    return jsonify({'ok': 1})