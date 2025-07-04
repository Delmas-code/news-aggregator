from geo_localiser import main_localiser
from analyzer import analyze_news_article

def main(news_data):
    localiser_data = main_localiser(news_data)
    if not localiser_data:
        return None
    
    analyses = analyze_news_article(news_data)
    
    final_output = {
        "id": "generate_id",
        "title": news_data["title"],
        "body": news_data["body"],
        "url": news_data["url"],
        "service_provide": "news_aggregator",
        "image_url": news_data["image_url"],
        "article_id": analyses["article_id"],
        "determined_topic": analyses["determined_topic"],
        "sentiment": analyses["sentiment"],
        "sentiment_level": analyses["sentiment_level"],
        "location": localiser_data
    }
    
    return final_output
    