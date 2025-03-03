

from app.configurations.mongodb.connect import ConnectMongoDB
from app.configurations.logging import logging
from app.constants.mongodb_constant import DATABASE_NAME,USERS_COLLECTIONS
from app.components.news import News
from app.components.jobs import Jobs

class Recommendation:

    def __init__(self,user_id):
        self.user_profile = self.users_collection.find_one({"_id":user_id})
        self.db = ConnectMongoDB(DATABASE_NAME)
        self.users_collection = self.db.get_collection(USERS_COLLECTIONS)
    
    def get_news_recommendation(self):
        try:
            news = News()
            get_news = news.get_news(self.user_profile)
            return get_news
        except Exception as e:
            logging.error(f"Error in getting news recommendation {e}")
            return None

    def get_jobs_recommendation(self):
        try:
            jobs = Jobs()
            get_jobs = jobs.get_jobs(self.user_profile)
            return get_jobs
        except Exception as e:
            logging.error(f"Error in getting news recommendation {e}")
            return None
    
    def get_recommendation(self):
        jobs = self.get_jobs_recommendation()
        news = self.get_news_recommendation()
        return jobs,news