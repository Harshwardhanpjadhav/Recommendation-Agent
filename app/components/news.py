from newsapi import NewsApiClient
from datetime import datetime, timezone
from app.configurations.logging import logging
from app.configurations.exception import CustomException

class News:

    def __init__(self):
        self.newsapi = NewsApiClient(api_key='1ad5fce26f95420cb7acf97f37fafebb')

    def fetch_news_for_interest(self, interest, lan):
        """
        Fetch news articles from NewsAPI's 'everything' endpoint for a given interest and language.
        """
        try:
            response = self.newsapi.get_everything(q=interest, language=lan)
            articles = response.get("articles", [])
            news_list = []
            for article in articles:
                title = article.get("title")
                description = article.get("description") or ""
                published_at_str = article.get("publishedAt", "")
                try:
                    published_date = datetime.fromisoformat(published_at_str.rstrip("Z"))
                    if published_date.tzinfo is None:
                        published_date = published_date.replace(tzinfo=timezone.utc)
                except CustomException as e:
                    logging.error(f"Date parsing error: {e}")
                    published_date = None
                url = article.get("url")
                source = article.get("source", {}).get("name", "NewsAPI")

                if title and published_date:
                    news_list.append({
                        "title": title,
                        "description": description,
                        "published_date": published_date,
                        "source": source,
                        "url": url
                    })
            return news_list
        except CustomException as e:
            logging.error(e)
            return False

    def calculate_final_score(self, article, user_interests):
        try:
            base_relevance = 0.8
            score = base_relevance

            title_lower = article["title"].lower()
            description_lower = article["description"].lower() if article["description"] else ""

            for interest in user_interests:
                interest_lower = interest.lower()
                if interest_lower in title_lower or interest_lower in description_lower:
                    score += 0.2  # bonus per matching interest

            now = datetime.now(timezone.utc)
            time_diff = now - article["published_date"]
            if time_diff.total_seconds() < 3600:
                score += 0.1
            elif time_diff.total_seconds() < 10800:
                score += 0.05

            return score
        except CustomException as e:
            logging.error(e)
            return False

    def fetch_news_based_on_profile(self, user_profile):
        try:
            aggregated_news = []
            # Get language preference from user profile, defaulting to 'en'
            language = user_profile.get("preferences", {}).get("language", "en")
            
            for interest in user_profile.get("interests", []):
                articles = self.fetch_news_for_interest(interest, language)
                if articles:
                    aggregated_news.extend(articles)

            seen_urls = set()
            unique_news = []
            for article in aggregated_news:
                if article["url"] and article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    unique_news.append(article)

            user_interests = user_profile.get("interests", [])
            for article in unique_news:
                article["final_score"] = self.calculate_final_score(article, user_interests)

            ranked_news = sorted(unique_news, key=lambda x: x["final_score"], reverse=True)

            max_recs = user_profile.get("preferences", {}).get("max_recommendations", len(ranked_news))
            return ranked_news[:max_recs]
        except CustomException as e:
            logging.error(e)
            return False

    def get_news(self, user_profile):
        try:
            news_recommendations = self.fetch_news_based_on_profile(user_profile)
            news_dict = {}
            for i, news in enumerate(news_recommendations, start=1):
                news_dict[f"news_{i}"] = {
                    "published_date": news["published_date"].strftime("%Y-%m-%d %H:%M:%S"),
                    "title": news["title"],
                    "final_score": news["final_score"],
                    "source": news["source"],
                    "url": news["url"]
                }
            return news_dict
        except CustomException as e:
            logging.error(e)
            return False
