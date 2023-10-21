from pymongo.mongo_client import MongoClient


class MongoDBCollection(dict):
    def __init__(self, db_name, collection_name, connect_string=None, unique_key="_id"):
        self.client = MongoClient(connect_string)
        try:
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]
        self.unique_key = unique_key
        self.load_data()

    def load_data(self):
        data = {
            item[self.unique_key]: MongoDBDocument(
                item, self.collection, self.unique_key
            )
            for item in self.collection.find({})
        }
        self.update(data)

    def find_by_key(self, key, value):
        query = {key: value}
        return self.collection.find_one(query)

    def delete(self, key):
        query = {self.unique_key: key}
        self.collection.delete_one(query)
        if key in self:
            del self[key]


    def __setitem__(self, key, value):
        value[self.unique_key] = key
        if key in self:
            existing_document = self[key]
            existing_document.update(value)
        else:
            self.update({key: MongoDBDocument(value, self.collection, self.unique_key)})


class MongoDBDocument(dict):
    def __init__(self, data, collection, unique_key):
        self.collection = collection
        self.unique_key = unique_key
        self.update(data)

    def save(self):
        query = {self.unique_key: self[self.unique_key]}
        update = {"$set": self}
        self.collection.update_one(query, update, upsert=True)

    def load(self):
        query = {self.unique_key: self[self.unique_key]}
        data = self.collection.find_one(query)
        if data:
            self.update(data)
