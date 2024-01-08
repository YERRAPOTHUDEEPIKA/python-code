import multiprocessing

# Function to be executed by each process
def update_shared_dict(shared_dict, key, value):
    shared_dict[key] = value

if __name__ == "__main__":
    # Create a shared memory manager
    manager = multiprocessing.Manager()

    # Create a shared dictionary
    shared_dict = manager.dict()

    # Create multiple processes to update the shared dictionary
    processes = []
    for i in range(5):
        process = multiprocessing.Process(target=update_shared_dict, args=(shared_dict, f'key{i}', f'value{i}'))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Print the shared dictionary
    print("Shared Dictionary:", shared_dict)
