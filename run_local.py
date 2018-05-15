#!flask/bin/python

"""
This file is part of MISPRINT.

MISPRINT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MISPRINT.  If not, see <http://www.gnu.org/licenses/>.
"""

from app import app
from app import socketio

#print "5"
app.debug=True

try:
    socketio.run(app, host=app.config['GLOBAL_HOST'], port = app.config['GLOBAL_PORT'])
except KeyboardInterrupt:
    print "Development Mode Exited"
#app.run(host=app.config['GLOBAL_HOST'], port = app.config['GLOBAL_PORT'], debug = app.config['DEBUG'])

