import multiprocessing
import socket
import pickle

def send_shared_dict(shared_dict, host, port):
    try:
        # Create a socket connection to the receiver program
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # Serialize and send the shared dictionary
            shared_dict_serialized = pickle.dumps(shared_dict)
            s.sendall(shared_dict_serialized)

    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    # Populate the shared dictionary with data
    shared_dict['key1'] = 'value1'
    shared_dict['key2'] = 'value2'

    host = 'localhost'
    port = 12345


    send_shared_dict(shared_dict, host, port)
