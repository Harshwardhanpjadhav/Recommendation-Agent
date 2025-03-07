
from app.configurations.mongodb.connect import ConnectMongoDB
from app.configurations.logging import logging
from app.constants.mongodb_constant import DATABASE_NAME,USERS_COLLECTIONS
from uuid import uuid4  
from app.configurations.exception import CustomException

class UsersDetail:
    def __init__(self):
        try:
            self.db = ConnectMongoDB(DATABASE_NAME)
            self.users_collection = self.db.get_collection(USERS_COLLECTIONS)
        except CustomException as e:
            logging.error(e)
            return False

    def add_users_details(self,data):
        try:
            user_data = {
                "user_id": data.user_id,
                "interests":data.interests,
                "preferences": data.preferences,
                "demographics": data.demographics
            }
            self.users_collection.insert_one(user_data)
            return {
                    "message": "Profile submitted successfully",
                    "user_id": data.user_id
                    }
        except CustomException as e:
            logging.error(e)
            return False



