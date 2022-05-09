from flask import Flask
app = Flask(__name__) 

from flask_socketio import SocketIO
socketio = SocketIO(app)

from app import views #to avoid circular import after defigning app
from app import api_views 
from app import sockets
