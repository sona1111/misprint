import gevent.monkey
gevent.monkey.patch_all()

from flask import Flask
from flask_mail import Mail
from sessions import MongoSessionInterface
from flask.ext.socketio import SocketIO
import logging.config



app = Flask(__name__)

#print "1"

app.config.from_pyfile('../config.py')

logging.getLogger('watchdog').setLevel(logging.WARNING)
logging.config.fileConfig(app.config['LOG_CONFIG_FILE'])
logr = logging.getLogger(__name__)

app.session_interface = MongoSessionInterface(app.config['MONGO_HOST'], app.config['MONGO_PORT'], app.config['MONGO_DATABASE'], app.config['MONGO_USER'], app.config['MONGO_PASS'])
mail=Mail(app)

socketio = SocketIO(app)

#print "2"

from app import views

#print "3"

