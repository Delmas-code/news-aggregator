import json
from classifier import classifier
from entity_engine import news_samples

def get_sentiment_level(sentiment_data):
    """
    Determines a sentiment level (high, medium, low, neutral) based on
    the sentiment label and its confidence score.
    """
    if not sentiment_data:
        return 'unknown'

    # Taking the first sentiment entry (assuming most relevant)
    sentiment_info = sentiment_data[0]
    label = sentiment_info['label'].lower()
    score = sentiment_info['score']
    """
    -1: unknown
    0: neutral
    1: low
    2: medium
    3: high
    """

    if label == 'neutral':
        return 'neutral', 0
    
    elif label == 'positive':
        if score >= 0.8: 
            return 'positive', 3
        elif score >= 0.5:
            return 'positive', 2
        else:
            return 'positive', 1
        
    elif label == 'negative':
        if score >= 0.8:
            return 'negative', 3
        elif score >= 0.5: 
            return 'negative', 2
        else:
            return 'negative', 1
    return 'unknown'


def analyze_news_article(news_data):
    """
    Analyzes a single news article to determine its topic and sentiment level.

    Args:
        news_data (dict): A dictionary representing the news article.

    Returns:
        dict: A dictionary containing the determined topic, sentiment level,
              and original article ID.
    """
    article_id = news_data.get('id')
    title = news_data.get('title', '')
    body = news_data.get('body', '')
    sentiment_raw = news_data.get('sentiment', [])

    # Determine the topic
    article = f"{title}. {body}"
    predicted_topic = classifier(article)

    
    # Determine the sentiment level
    sentiment, sentiment_level = get_sentiment_level(sentiment_raw)

    return {
        "article_id": article_id,
        "determined_topic": predicted_topic,
        "sentiment": sentiment,
        "sentiment_level": sentiment_level
    }

# if __name__ == '__main__':
#     analysis_result = analyze_news_article(news_samples.sample_news_article_1)
#     print("\nAnalysis Result:")
#     print(json.dumps(analysis_result, indent=4))