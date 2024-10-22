from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import connect_to_database, disconnect_from_database, init_db
from app.api import (
    source,
    content,
    webhook,
    notification,
    transcription,
    tag,
    category,
    recognition,
)

# Service gateway
from app.services.services import main as get_articles
from app.services.nlp.main import check_queue as nlp_check_queue
from app.services.persistence.main import check_queue as persistence_check_queue

from loguru import logger

# logger configuration
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO")

app = FastAPI(docs_url="/docs", title="News feed Aggregator")

scheduler = AsyncIOScheduler()

MINUTES = 5


@app.on_event("startup")
async def startup() -> None:
    """Initialize database connection and tables."""
    try:
        await connect_to_database()
        await init_db()
        logger.info("Database connection established")

        scheduler.add_job(get_articles, "interval", minutes=MINUTES * 0.35)
        scheduler.add_job(nlp_check_queue, "interval", minutes=MINUTES * 0.4)
        scheduler.add_job(persistence_check_queue, "interval", minutes=MINUTES * 0.35)
        scheduler.start()
        logger.info("Sheduler started")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Close database connection."""
    try:
        await disconnect_from_database()
        scheduler.shutdown(wait=False)
        logger.info("Database Connection and cron stopped")
    except Exception as e:
        logger.error(f"Error shutting down: {e}")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(source.router, prefix="/sources", tags=["sources"])
app.include_router(content.router, prefix="/contents", tags=["contents"])
app.include_router(webhook.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(notification.router, prefix="/notifications", tags=["notifications"])
app.include_router(
    transcription.router, prefix="/transcriptions", tags=["transcriptions"]
)
app.include_router(tag.router, prefix="/tags", tags=["tags"])
app.include_router(category.router, prefix="/categories", tags=["categories"])
app.include_router(recognition.router, prefix="/recognitions", tags=["recognitions"])
