from fastapi import FastAPI

from app.core.database import (
    connect_to_database,
    disconnect_from_database,
    init_db
)
from app.services.rss import rss_parser
from app.api import source, content
from loguru import logger

import uvicorn

# logger configuration
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO")

app = FastAPI(docs_url="/docs", title="News feed Aggregator")

@app.on_event("startup")
async def startup() -> None:
    """start the rss service"""
    await rss_parser.main()

    """Initialize database connection and tables."""
    try:
        await connect_to_database()
        await init_db()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")

@app.on_event("shutdown")
async def shutdown() -> None:
    """Close database connection."""
    try:
        await disconnect_from_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")



@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.include_router(source.router, prefix="/sources", tags=["sources"])
app.include_router(content.router, prefix="/contents", tags=["contents"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
 
