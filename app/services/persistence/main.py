import asyncio
import aio_pika
import json
import os
import traceback

from loguru import logger
from dotenv import load_dotenv

from app.crud.content import create_content
from app.schemas.content import ContentCreate

from ...core.database import get_db

load_dotenv()

# Contstants
RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def save_content_to_db(article: ContentCreate):
    try:
        async for db in get_db():
            await create_content(db, article)
            logger.info(f"Saved content to database: {article['title']}")
    except KeyError as e:
        logger.error(f"Missing key in content: {e}")
    except Exception as e:
        logger.error(f"Error saving content to database: {e}")


async def check_queue():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("persistence", auto_delete=False)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode()
                    try:
                        articles = json.loads(body)
                        if not isinstance(articles, list):
                            logger.error(f"Invalid content format: {body}")
                            continue
                        for article in articles:
                            await save_content_to_db(article)

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error(f"Error processing message: {e}")
