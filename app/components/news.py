
from newsapi import NewsApiClient
from datetime import datetime, timezone
class News:

    def __init__(self):
        self.newsapi = NewsApiClient(api_key='1ad5fce26f95420cb7acf97f37fafebb')

    def fetch_news_for_interest(self,interest):
        """
        Fetch news articles from NewsAPI's 'everything' endpoint for a given interest.
        """
        response = self.newsapi.get_everything(q=interest,language='en')
        
        articles = response.get("articles", [])
        news_list = []
        for article in articles:
            title = article.get("title")
            description = article.get("description") or ""
            published_at_str = article.get("publishedAt", "")
            try:
                # Convert ISO 8601 string to datetime; remove trailing 'Z' if present.
                published_date = datetime.fromisoformat(published_at_str.rstrip("Z"))
                # Assume the date is in UTC if no timezone info provided.
                if published_date.tzinfo is None:
                    published_date = published_date.replace(tzinfo=timezone.utc)
            except Exception as e:
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

    def calculate_final_score(self,article, user_interests):
        """
        Calculates a final score for an article based on:
        - A base relevance score (constant).
        - Boost for matching any user interest in the title or description.
        - A recency bonus based on how recent the article is.
        """
        # Constant base relevance for all articles
        base_relevance = 0.8
        score = base_relevance
        
        # Lowercase the title and description for matching
        title_lower = article["title"].lower()
        description_lower = article["description"].lower() if article["description"] else ""
        
        # Boost for each matching interest keyword found in title or description
        for interest in user_interests:
            interest_lower = interest.lower()
            if interest_lower in title_lower or interest_lower in description_lower:
                score += 0.2  # bonus per matching interest
        
        # Recency bonus:
        # Compute the time difference between now and the article's published_date.
        now = datetime.now(timezone.utc)
        time_diff = now - article["published_date"]
        # If published within 1 hour, add 0.1; within 3 hours, add 0.05; else no bonus.
        if time_diff.total_seconds() < 3600:
            score += 0.1
        elif time_diff.total_seconds() < 10800:
            score += 0.05
        
        return score

    def fetch_news_based_on_profile(self,user_profile):
        """
        Aggregates news articles from NewsAPI based on each user interest,
        deduplicates them, computes a final ranking score, sorts by that score,
        and returns the top articles based on the user's max_recommendations preference.
        """
        aggregated_news = []
        
        # Fetch articles for each interest
        for interest in user_profile.get("interests", []):
            articles = self.fetch_news_for_interest(interest)
            aggregated_news.extend(articles)
        
        # Remove duplicates based on the article URL
        seen_urls = set()
        unique_news = []
        for article in aggregated_news:
            if article["url"] and article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_news.append(article)
        
        # Compute final ranking score for each article
        user_interests = user_profile.get("interests", [])
        for article in unique_news:
            article["final_score"] = self.calculate_final_score(article, user_interests)
        
        # Sort articles by final_score (most relevant first)
        ranked_news = sorted(unique_news, key=lambda x: x["final_score"], reverse=True)
        
        # Limit the results based on user's max_recommendations preference
        max_recs = user_profile.get("preferences", {}).get("max_recommendations", len(ranked_news))
        return ranked_news[:max_recs]

    def get_news(self,user_profile):
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