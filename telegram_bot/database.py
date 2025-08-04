from pymongo import MongoClient

# Función para establecer la conexión con la base de datos
def connect_to_database():
    client = MongoClient('localhost', 27017)
    return client['telegramBot']
# Función para insertar un documento en la colección
def insert_document(collection, data):
    collection.insert_one(data)

# Función para buscar un solo documento en la colección
def findDocument(collection, query):
    return collection.find_one(query)

# Función para buscar documentos en la colección
def findDocuments(collection, query):
    return collection.find(query)

# Función para actualizar un documento en la colección
def updateDocument(collection, query, new_data):
    collection.update_one(query, {"$set": new_data})

# Función para eliminar un documento de la colección
def deleteDocument(collection, query):
    collection.delete_one(query)

# Función para insertar o actualizar un documento en la colección
def upsertDocument(collection, query, data):
    result = collection.update_one(query, {"$set": data}, upsert=True)
    return result

def limpiarFlags():
    db = connect_to_database()
    collection = db['flags']
    filtro = {}
    collection.delete_many(filtro)