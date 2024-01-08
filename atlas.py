import pymongo

# Replace this connection string with your MongoDB Atlas connection string
# Example: "mongodb+srv://<username>:<password>@<your-cluster-url>/<dbname>?retryWrites=true&w=majority"
# Replace <username>, <password>, <your-cluster-url>, and <dbname> with your own credentials
connection_string = "mongodb+srv://yerrapothudeepika:Deepika2117@cluster0.8n3ryuc.mongodb.net/"

# Connect to MongoDB Atlas
try:
    client = pymongo.MongoClient(connection_string)
    print("Connected to MongoDB Atlas!")
    
    # List the available databases
    print("Available Databases:")
    print(client.list_database_names())
    
    # Access a specific database
    db = client.get_database('Data')  # Replace 'your_database_name' with your database name
    
    # Access a specific collection within the database
    collection = db['kappsoft']  # Replace 'your_collection_name' with your collection name
    
    # Perform operations (e.g., insert, find, update, delete) on the collection
    # For example, to insert a document
    data = {"name": "John", "age": 30, "email": "john@example.com"}
    collection.insert_one(data)
    
    # Find a document
    result = collection.find_one({"name": "John"})
    print("Found document:", result)
    
    # Update a document
    collection.update_one({"name": "John"}, {"$set": {"age": 31}})
    updated_result = collection.find_one({"name": "John"})
    print("Updated document:", updated_result)
    
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB Atlas: %s" % e)
