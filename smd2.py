import socket
import pickle

def receive_shared_dict(host, port):
    try:
        # Create a socket connection to listen for data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()

            print(f"Listening on {host}:{port}")

            conn, addr = s.accept()

            with conn:
                print(f"Connected by {addr}")

                # Receive and deserialize the shared dictionary
                shared_dict_serialized = conn.recv(4096)
                shared_dict = pickle.loads(shared_dict_serialized)

                print("Received Shared Dictionary:", shared_dict)

    except Exception as e:
        print(f"Error receiving data: {e}")

if __name__ == "__main__":
    host = 'localhost'
    port = 12345

    receive_shared_dict(host, port)
