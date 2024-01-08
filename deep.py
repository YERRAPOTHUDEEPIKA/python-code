from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secertkey'
app.config['DEBUG'] = True
socketio = SocketIO(app)




@socketio.on('message')
def receive_message(message):
	print('**************: {}'.format(message))
	send('this is a message from flask')


@socketio.on('custom event')
def receive_custom_event(message):
	print('The custom message is : {}'.format(message))
	emit('from flask','this is a custom event from flask.')

if __name__ == '__main__':
	socketio.run(app)

