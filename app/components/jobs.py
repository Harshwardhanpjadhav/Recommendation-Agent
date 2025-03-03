from datetime import datetime, timezone
from app.configurations.mongodb.connect import ConnectMongoDB
from app.configurations.logging import logging
from app.constants.mongodb_constant import DATABASE_NAME, JOBS


class Jobs:
    def __init__(self):
        self.db = ConnectMongoDB(DATABASE_NAME)
        self.jobs_collection = self.db.get_collection(JOBS)

    def get_posted_date(self, job):
        posted_date_val = job.get("job_posted_date", "")

        # If it's a dict (e.g., {"$date": "2025-02-24T04:30:19.596Z"})
        if isinstance(posted_date_val, dict):
            posted_date_str = posted_date_val.get("$date", "")
            try:
                dt = datetime.fromisoformat(posted_date_str.rstrip("Z"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception as e:
                return None
        # If it's already a datetime object
        elif isinstance(posted_date_val, datetime):
            dt = posted_date_val
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        # If it's a string
        elif isinstance(posted_date_val, str):
            try:
                dt = datetime.fromisoformat(posted_date_val.rstrip("Z"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception as e:
                return None
        return None

    def calculate_job_final_score(self, job, user_interests):
        # Base score for all jobs
        base_score = 0.7
        bonus = 0.0

        # Combine key text fields from the job posting and convert to lowercase
        fields_to_check = [
            job.get("job_title", ""),
            job.get("job_industries", ""),
            job.get("job_summary", "")
        ]
        combined_text = " ".join(fields_to_check).lower()

        # Add bonus for each matching interest keyword found in the text
        for interest in user_interests:
            if interest.lower() in combined_text:
                bonus += 0.3  # Increase bonus per match

        # Recency bonus: get the posted date using our helper function
        recency_bonus = 0.0
        posted_date = self.get_posted_date(job)
        if posted_date:
            now = datetime.now(timezone.utc)
            diff_hours = (now - posted_date).total_seconds() / 3600
            # Bonus if posted within 24 hours, or within one week
            if diff_hours < 24:
                recency_bonus = 0.2
            elif diff_hours < 168:  # less than a week
                recency_bonus = 0.1

        final_score = base_score + bonus + recency_bonus
        return final_score

    def rank_job_postings(self, job_postings, user_profile):
        """
        Rank job postings from the MongoDB collection based on a computed final score.
        Returns the top job postings as defined in the user's max_recommendations.
        """
        user_interests = user_profile.get("interests", [])
        for job in job_postings:
            job["final_score"] = self.calculate_job_final_score(job, user_interests)

        # Sort the jobs by final_score (highest first)
        ranked_jobs = sorted(
            job_postings, key=lambda x: x["final_score"], reverse=True)

        # Limit results based on the user's max_recommendations preference
        max_recs = user_profile.get("preferences", {}).get(
            "max_recommendations", len(ranked_jobs))
        return ranked_jobs[:max_recs]

    def get_jobs(self, user_profile):
        job_postings = list(self.jobs_collection.find({}))
        ranked_jobs = self.rank_job_postings(job_postings, user_profile)
        jobs_dict = {}
        for i, job in enumerate(ranked_jobs, start=1):
            posted_date = self.get_posted_date(job)
            posted_date_str = posted_date.strftime(
                "%Y-%m-%d %H:%M:%S") if posted_date else "N/A"
            jobs_dict[f"job_{i}"] = {
                "final_score": round(job["final_score"], 2),
                "job_title": job["job_title"],
                "company_name": job["company_name"],
                "posted_date": posted_date_str,
                "industry": job.get("job_industries", "N/A")
            }
        return jobs_dict
