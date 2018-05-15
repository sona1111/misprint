__author__ = 'paul'
import gevent.monkey
gevent.monkey.patch_all(subprocess=True)

from app import app
from celery import Celery
from app.functions import get_db_proc
from PrinterApi.Core import updateAll, getPrinterRecords
import json, urllib2




#queue = Celery('appssite', broker=app.config['CELERY_BROKER_URL'])
#queue.config_from_object("celeryconfig")

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery

#print "7"

queue = make_celery(app)

#print "8"



@queue.task
def checkPrinters():
    print "running Checkprinters"
    updateAll()
    PR = getPrinterRecords()
    data = PR.getAllImportant()
    payload = {'data':data}
    request = urllib2.Request('http://%s:%d/redirectOutput' % ('localhost', app.config['GLOBAL_PORT']))
    request.add_header('Content-Type', 'application/json')
    urllib2.urlopen(request, json.dumps(payload))



if __name__ == "__main__":
    checkPrinters()