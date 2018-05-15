from datetime import timedelta

DEBUG = True
CSRF_ENABLED = False
SECRET_KEY = 'pkmn123'

#SERVER SETTINGS
LOG_CONFIG_FILE = 'app/ini/log.ini.nofile'
GLOBAL_HOST = '0.0.0.0'
GLOBAL_PORT = 8000
#EMAIL SETTINGS
MAIL_DEBUG = False
MAIL_SERVER='smtp.office365.com'
MAIL_PORT=587
MAIL_USE_SSL=False
MAIL_USE_TLS=True
MAIL_USERNAME = 'saide@raritanval.edu'
MAIL_SENDER = "RVCC MIS Help Desk <saide@raritanval.edu>"
MAIL_PASSWORD = 'SA@123456'
MAIL_SUPPRESS_SEND = False
TICKET_CREATION_EMAILS = ["g00228389@stu.raritanval.edu", "mary.omara@raritanval.edu"]
TESTING = False

#MONGO_SETTINGS
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DATABASE = 'misprint'
MONGO_USER = None
MONGO_PASS = None

#CELERY SETTINGS
CELERY_ENABLE = True
CELERY_BROKER_URL = 'mongodb://localhost:27017/misprint'
CELERYBEAT_SCHEDULE = {
    'checkPrinters': {
        'task': 'app.taskQueue.checkPrinters',
        'schedule': timedelta(minutes=5),
    },
}
#CELERY_IMPORTS = ("app.taskQueue", )
