from app import app, socketio
from flask_socketio import SocketIO

if __name__ == "__main__":
    app.secret_key = ''
    app.debug = True
    socketio.run(app)



#pipreqs C:\Users\Sam\Desktop\coding\WordsOnline\newFlask\WordsOnline 
#for requirements pipreqs --force C:\Users\Sam\Desktop\coding\WordsOnline\newFlask\WordsOnline 
