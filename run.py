#!flask/bin/python
from app import app
from werkzeug.contrib.fixers import ProxyFix
#from app import socketio
import logging
app.wsgi_app = ProxyFix(app.wsgi_app)

#print "5"

#app = socketio.run(app)

#print "6"
#app.run(host=app.config['GLOBAL_HOST'], port = app.config['GLOBAL_PORT'], debug = app.config['DEBUG'])




if False: #__name__ == '__main__':
    #print "7"
    #app.run()

    PORT=8000
    app.debug = False
    logging.getLogger(__name__).setLevel(logging.WARNING)
    app.config['GLOBAL_PORT'] = PORT

    try:
        print "Gevent Server Running %s:%d" % (app.config['GLOBAL_HOST'], PORT)
        
        #socketio.run(app, host=app.config['GLOBAL_HOST'], port = PORT)
    except KeyboardInterrupt:
        print "Production Mode Exited"
    except:
        print "Unhandled Mode Exit"

