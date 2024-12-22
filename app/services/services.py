import os
import sys
import json
import asyncio
import aio_pika

from app.crud import source as source_crud
from app.services.assets.source_serializer import user_schema
from app.core.database import get_db

from .rss.rss_parser import main as rss_main
from .audiotranscription.audio import main as audio_main

from loguru import logger
from dotenv import load_dotenv

current_dir = os.getcwd()
sys.path.append(current_dir)

load_dotenv()

# Contstants
RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def publish_message(channel, message, routing_key="articles"):
    try:
        if message:
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()), routing_key=routing_key
            )
        else:
            logger.warning("Skipping empty message, nothing to publish")
    except Exception as e:
        logger.error(f"Error publishing message: {e}")


async def process_item(channel, item):
    serialized_item = user_schema.dump(item)
    type = serialized_item.get("type")

    try:
        if type in ["rss", "feed"]:
            result = await rss_main(serialized_item)
        elif type in ["audio", "video"]:
            result = await audio_main(serialized_item)

        else:
            logger.error(f"Unsupported type: {type}")
            return

        if result:
            serialized_result = json.dumps(result)
            await publish_message(channel, serialized_result)
        else:
            logger.warning(f"Skipping empty result for item: {item}")
    except Exception as e:
        logger.error(f"Error processing item: {item}. Error: {e}")


async def process_batch(batch, channel):
    try:
        tasks = [process_item(channel, item) for item in batch]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error processing batch: {e}")


async def main():
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue("articles")

            async for db_session in get_db():
                async for batch in source_crud.get_sources_in_batch(
                    db_session, limit=10
                ):
                    await process_batch(batch, channel)
    except Exception as e:
        logger.error(f"Error in processing batches: {e}")
