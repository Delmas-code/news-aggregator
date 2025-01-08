import asyncio
import aio_pika
import json
import torch
import re
import traceback
import os
import numpy as np

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MODEL_NAME = "microsoft/deberta-v3-small"

# Dev
# MODELS_PATH = os.path.join(os.path.dirname(__file__), "models/")
# TONE_MODEL_PATH = os.path.join(MODELS_PATH, "tone/")
# CATEGORY_MODEL_PATH = os.path.join(MODELS_PATH, "category/")

# Prod
TONE_MODEL_PATH = "ngenge/tone_classifier"
CATEGORY_MODEL_PATH = "ngenge/nlp_processor" # for multilabel classification

LABELS_PATH = os.path.join(os.path.dirname(__file__), "labels")
THRESHOLD_RANGES = {
    (0.1, 0.3): 1,
    (0.3, 0.4): 2,
    (0.4, 1.0): 3,
}

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load labels
with open(os.path.join(LABELS_PATH, "tones.json"), "r") as f:
    id2tone = json.load(f)["id2tone"]

with open(os.path.join(LABELS_PATH, "categories.json"), "r") as f:
    id2category = json.load(f)["id2category"]

# Load models and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, clean_up_tokenization_spaces=True)

ner_model = pipeline(
    "token-classification",
    model="dslim/bert-base-NER",
    device=device
)

sentiment_model = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device=device,
)

category_model = AutoModelForSequenceClassification.from_pretrained(
    CATEGORY_MODEL_PATH
).to(device)

tone_model = AutoModelForSequenceClassification.from_pretrained(TONE_MODEL_PATH).to(
    device
)


# Utility functions
def clean_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"[^a-zA-Z\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def convert_to_native_types(obj):
    if isinstance(obj, torch.Tensor):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    return obj


class DynamicLabelSelector:
    def __init__(self, model, labels):
        self.model = model
        self.labels = labels

    def make_predictions(self, text):
        inputs = tokenizer(
            text, truncation=True, max_length=768, return_tensors="pt", padding=True
        ).to(device)
        outputs = self.model(**inputs)
        return torch.sigmoid(outputs.logits)

    def dynamic_label_selection(self, predictions):
        predictions = predictions.squeeze()
        sorted_preds, sorted_indices = torch.sort(predictions, descending=True)
        for (min_threshold, max_threshold), count in THRESHOLD_RANGES.items():
            if (
                sorted_preds[0].item() >= min_threshold
                and sorted_preds[count - 1].item() <= max_threshold
            ):
                selected_indices = sorted_indices[:count]
                return [self.labels[str(idx.item())] for idx in selected_indices]
        return [self.labels[sorted_indices[0].item()]]

    def predict(self, text):
        predictions = self.make_predictions(text)
        return self.dynamic_label_selection(predictions)


async def process_article(article):
    try:
        text = article["title"] + " " + article["body"]
        text = clean_text(text)
        tone_selector = DynamicLabelSelector(tone_model, id2tone)
        category_selector = DynamicLabelSelector(category_model, id2category)

        tones = tone_selector.predict(text)
        categories = category_selector.predict(text)
        sentiment = sentiment_model(text)
        entities = ner_model(text)

        return {
            "source_id": article["source_id"],
            "url": article["url"],
            "image_url": article["image_url"],
            "title": article["title"],
            "type": article["type"],
            "body": article["body"],
            "flags": tones,
            "tags": categories,
            "sentiment": sentiment,
            "entities": entities,
        }
    except Exception as e:
        logger.error(f"Error processing article: {e}")
        logger.error(traceback.format_exc())
        return None


async def process_article_batch(articles):
    tasks = [process_article(article) for article in articles]
    return [article for article in await asyncio.gather(*tasks) if article is not None]


async def send_to_persistence_layer(article, channel):
    try:
        persistence_queue = await channel.declare_queue("persistence", auto_delete=False)
        
        if article:
            await channel.default_exchange.publish(
                aio_pika.Message(body=article.encode()),
                routing_key=persistence_queue.name,
            )
        else:
            logger.warning("Skipping empty message, nothing to publish")
            
    except Exception as e:
        logger.error(f"Error publishing message: {e}")


async def check_queue():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("articles", auto_delete=False)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        articles = json.loads(message.body.decode())
                        if not articles:
                            logger.error("Received empty message")
                            return None
                        processed_articles = await process_article_batch(articles)
                        processed_articles = [
                            convert_to_native_types(article)
                            for article in processed_articles
                        ]
                        processed_articles_json = json.dumps(
                            processed_articles, default=str
                        )
                        
                        
                        await send_to_persistence_layer(
                            processed_articles_json, channel
                        )

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error(f"Error processing message: {e}")
