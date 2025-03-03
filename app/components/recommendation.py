

from app.configurations.mongodb.connect import ConnectMongoDB
from app.configurations.logging import logging
from app.constants.mongodb_constant import DATABASE_NAME,USERS_COLLECTIONS
from app.components.news import News
from app.configurations.exception import CustomException

from app.components.jobs import Jobs

class Recommendation:

    def __init__(self,user_id):
        try:
            self.db = ConnectMongoDB(DATABASE_NAME)
            self.users_collection = self.db.get_collection(USERS_COLLECTIONS)
            self.user_profile = self.users_collection.find_one({"user_id":user_id})
            logging.info(f"Users details {self.users_collection}")
        except CustomException as e:
            logging.error(e)
            return False
    
    def get_news_recommendation(self):
        try:
            news = News()
            get_news = news.get_news(self.user_profile)
            return get_news
        except CustomException as e:
            logging.error(f"Error in getting news recommendation {e}")
            return None

    def get_jobs_recommendation(self):
        try:
            jobs = Jobs()
            get_jobs = jobs.get_jobs(self.user_profile)
            return get_jobs
        except CustomException as e:
            logging.error(f"Error in getting job recommendation {e}")
            return None
    
    def get_recommendation(self):
        try:
            jobs = self.get_jobs_recommendation()
            news = self.get_news_recommendation()
            return jobs,news
        except CustomException as e:
            logging.error(e)
            return False