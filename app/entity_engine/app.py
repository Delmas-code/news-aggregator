# tasks.py
import os
from celery import Celery
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from geo_localiser import main_localiser
from analyzer import analyze_news_article
from datetime import datetime, timezone

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

NEWS_AGGRE = os.getenv("DEV_DATABASE_URL")
LIM_DB = os.getenv("LIM_DB_URL")

celery_app = Celery("sentiment_localiser", broker=RABBITMQ_URL)

@celery_app.task
def process_data():
    print("Job started: reading from news aggre DB")

    conn_a = psycopg2.connect(NEWS_AGGRE)
    conn_b = psycopg2.connect(LIM_DB)

    try:
        
        # Get all source rows from NEWS_AGGRE
        cur_a = conn_a.cursor()
        cur_a.execute("SELECT * FROM contents;")
        source_rows = cur_a.fetchall()

        print(f"Fetched {len(source_rows)} rows from NEWS_AGGRE")

        # Get all existing article_ids from LIM_DB: news_content table
        cur_b = conn_b.cursor()
        
        cur_b.execute("""
            CREATE TABLE IF NOT EXISTS news_content(
                id STRING NOT NULL PRIMARY KEY,
                title STRING,
                body STRING,
                url STRING,
                image_url STRING,
                service_provide STRING,
                article_id STRING,
                determined_topic STRING,
                sentiment FLOAT,
                sentiment_level STRING,
                location JSON,
                created_at DATETIME,
                updated_at DATETIME
            )
        """)
        cur_b.execute("SELECT article_id FROM news_content;")
        existing_ids = {row[0] for row in cur_b.fetchall()}

        print(f"Found {len(existing_ids)} existing article_ids in LIM_DB")

        # Filter new rows
        new_rows = [row for row in source_rows if row[0] not in existing_ids]

        print(f"{len(new_rows)} new rows to process")

        if not new_rows:
            print("Nothing new to do, exiting.")
            return

        # Process new rows
        processed_results = []
            
        for news_data in new_rows:
            localiser_data = main_localiser(news_data)
            if not localiser_data:
                continue
            
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
                "location": localiser_data,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            processed_results.append(final_output)
        
        processed_rows = [
            (d["id"], d["title"], d["body"], d["url"], d["image_url"],
             d["service_provide"], d["article_id"], d["determined_topic"],
             d["sentiment"], d["sentiment_level"], d["location"], d["created_at"], d["updated_at"]
             ) for d in process_data
        ]

        
        print(f"Processed {len(processed_results)} rows")

        # Insert results into LIM_DB: news_content table
        insert_query = """
            INSERT INTO news_content ()
            VALUES %s
        """
        execute_values(cur_b, insert_query, processed_rows)

        conn_b.commit()

        print("Inserted new results and updated article_ids")

    finally:
        conn_a.close()
        conn_b.close()

    print("Job finished.")
    
    
celery_app.config_from_object("celeryconfig")
