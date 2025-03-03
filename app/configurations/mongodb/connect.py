from app.constants.mongodb_constant import *
import pymongo
from app.configurations.exception import CustomException
from app.constants.env_variables import EvironmentVariable as ev
import sys


class ConnectMongoDB:
    client = pymongo.MongoClient(ev.mongo_url)
    def __init__(self, database_name):
        try:
            self.db = self.client[database_name]
            # self.collection = self.db[collection_name]
        except Exception as e:
            logging.error(e)
            return False

    def get_collection(self, collection_name):
        try:
            self.collection = self.db[collection_name]
            return self.collection
        except Exception as e:
            return False
