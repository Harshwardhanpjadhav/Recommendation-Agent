from datetime import datetime, timezone
from app.configurations.mongodb.connect import ConnectMongoDB
from app.configurations.logging import logging
from app.constants.mongodb_constant import DATABASE_NAME, JOBS
from app.configurations.exception import CustomException

class Jobs:
    def __init__(self):
        try:
            self.db = ConnectMongoDB(DATABASE_NAME)
            self.jobs_collection = self.db.get_collection(JOBS)
        except CustomException as e:
            logging.error(e)
            return False

    def get_posted_date(self, job):
        try:
            posted_date_val = job.get("job_posted_date", "")
            if isinstance(posted_date_val, dict):
                posted_date_str = posted_date_val.get("$date", "")
                try:
                    dt = datetime.fromisoformat(posted_date_str.rstrip("Z"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except Exception as e:
                    return None
            elif isinstance(posted_date_val, datetime):
                dt = posted_date_val
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            elif isinstance(posted_date_val, str):
                try:
                    dt = datetime.fromisoformat(posted_date_val.rstrip("Z"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except Exception as e:
                    return None
            return None
        except CustomException as e:
            logging.error(e)
            return False

    def calculate_job_final_score(self, job, user_interests, user_demographics):
        try:
            base_score = 0.7
            bonus = 0.0

            # Combine key text fields from the job posting
            fields_to_check = [
                job.get("job_title", ""),
                job.get("job_industries", ""),
                job.get("job_summary", "")
            ]
            combined_text = " ".join(fields_to_check).lower()

            # Bonus for matching any of the user's interests
            for interest in user_interests:
                if interest.lower() in combined_text:
                    bonus += 0.3  # bonus per matching interest

            # Demographic bonus: check user's location
            user_location = user_demographics.get("location", "").lower()
            job_location = job.get("job_location", "").lower() if job.get("job_location") else ""
            if user_location and job_location and user_location in job_location:
                bonus += 0.2

            # Demographic bonus: check if user's occupation is mentioned
            user_occupation = user_demographics.get("occupation", "").lower()
            if user_occupation and user_occupation in combined_text:
                bonus += 0.2

            # Recency bonus based on job posting date
            recency_bonus = 0.0
            posted_date = self.get_posted_date(job)
            if posted_date:
                now = datetime.now(timezone.utc)
                diff_hours = (now - posted_date).total_seconds() / 3600
                if diff_hours < 24:
                    recency_bonus = 0.2
                elif diff_hours < 168:  # less than a week
                    recency_bonus = 0.1

            final_score = base_score + bonus + recency_bonus
            return final_score
        except CustomException as e:
            logging.error(e)
            return False

    def rank_job_postings(self, job_postings, user_profile):
        """
        Rank job postings from the MongoDB collection based on a computed final score.
        The final score is computed using:
         - A base score
         - Bonuses for matching user interests in job text
         - Bonuses for matching demographics: location and occupation
         - A recency bonus based on the job's posted date
        Returns the top job postings as defined in the user's max_recommendations.
        """
        try:
            user_interests = user_profile.get("interests", [])
            user_demographics = user_profile.get("demographics", {})
            for job in job_postings:
                job["final_score"] = self.calculate_job_final_score(job, user_interests, user_demographics)

            ranked_jobs = sorted(job_postings, key=lambda x: x["final_score"], reverse=True)
            max_recs = user_profile.get("preferences", {}).get("max_recommendations", len(ranked_jobs))
            return ranked_jobs[:max_recs]
        except CustomException as e:
            logging.error(e)
            return False

    def get_jobs(self, user_profile):
        try:
            job_postings = list(self.jobs_collection.find({}))
            ranked_jobs = self.rank_job_postings(job_postings, user_profile)
            jobs_dict = {}
            for i, job in enumerate(ranked_jobs, start=1):
                posted_date = self.get_posted_date(job)
                posted_date_str = posted_date.strftime("%Y-%m-%d %H:%M:%S") if posted_date else "N/A"
                jobs_dict[f"job_{i}"] = {
                    "final_score": round(job["final_score"], 2),
                    "job_title": job["job_title"],
                    "company_name": job["company_name"],
                    "posted_date": posted_date_str,
                    "industry": job.get("job_industries", "N/A")
                }
            return jobs_dict
        except CustomException as e:
            logging.error(e)
            return False
