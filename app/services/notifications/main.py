from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from ...crud.webhook import get_specific_column
from ...models.webhook import Webhook
from ...core.database import get_db
from loguru import logger

import requests


async def send_webhooks(urls: list[str]):

    for url in urls:
        try:
            requests.post(url, json={"time": datetime.now().isoformat()})
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            


async def get_hooks():
    try:
        async for db in get_db():
            urls = await get_specific_column(db, "url")
            return urls
            logger.info("Urls working correctly")
    except Exception as e:
        logger.error(f"Error saving content to database: {e}")
