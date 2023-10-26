import pymongo
import json
import certifi
# Mongo client Debugging: 
# Tsl error :https://stackoverflow.com/questions/54484890/ssl-handshake-issue-with-pymongo-on-python3
# Ip address whilisting mongo atlas..
class ImportCSV:
    def __init__(self,database,maindb=0) -> None:
        ca = certifi.where()
        # This tells python to specifically send a tls certificate for the connection.
        if maindb == 0: # User Accounts Database
            # mongodb+srv://palondomus:kya63amari@revisionbank0.elhfgsw.mongodb.net/?retryWrites=true&w=majority
            # 
            client = pymongo.MongoClient(f"mongodb+srv://palondrome:kya63amari@roadmaptestcluster0.avksy.mongodb.net/roadmaptestdb?retryWrites=true&w=majority",tlsCAFile=ca)
            self.db = client[database]
        elif maindb == 1:# Question Paper 1 Database
            client = pymongo.MongoClient(f"mongodb+srv://palondrome2:kya63amari@cluster0.rxqjf.mongodb.net/chemistryqp?retryWrites=true&w=majority",tlsCAFile=ca)
            self.db = client[database]
        elif maindb == 2:# Question Paper 1 Database
            client = pymongo.MongoClient(f"mongodb+srv://palondrome3:kya63amari@qpcluster1.iplrmml.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)
            self.db = client[database]
    def load_data(self,collection_name,init_data):
        # Initialises collection 
        db_cm = self.db[collection_name]
        def load_n_insert(data):
            # Input is Dataframe
            data_json = json.loads(data.to_json(orient='records'))
            db_cm.insert_many(data_json)
        load_n_insert(init_data)
