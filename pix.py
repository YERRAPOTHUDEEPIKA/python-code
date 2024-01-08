import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

# Define an event handler for the 'connect' event
@sio.on('connect')
def on_connect():
    print("Connected to the Socket.IO server")

# Define an event handler for the 'message' event
@sio.on('message')
def on_message(data):
    print(f"Received message from server: {data}")

# Define an event handler for the 'disconnect' event
@sio.on('disconnect')
def on_disconnect():
    print("Disconnected from the Socket.IO server")

if __name__ == '__main__':
    # Connect to the Socket.IO server
    server_url = 'wss://exchange-websocket.unicoindcx.com/ticker'  # Replace with your actual server URL
    sio.connect(server_url)

    while True:
        message = input("Enter a message (or 'exit' to quit): ")
        if message == 'exit':
            break
        # Send the message to the server
        sio.emit('message', message)

    # Disconnect from the server when done
    sio.disconnect()
