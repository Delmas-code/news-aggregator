import os, sys, asyncio
current_dir = os.getcwd()
sys.path.append(current_dir)

from dotenv import load_dotenv
from app.services.assets.crud_manager import (
    get_sources_in_batch, 
    create_item, 
    get_source_item_ids
)
from loguru import logger
import assemblyai as aai
from extraction import ContentAnalyzer
from app.schemas.content import ContentCreate

load_dotenv()

class AssemblyAIHelper:
    def __init__(self, api_key):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()

    def transcribe(self, file_url):
        transcript = self.transcriber.transcribe(file_url)

        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"Error transcribing {file_url}: {transcript.error}")
            return None

        return transcript.text

    def analyze_sentiment(self, file_url):
        config = aai.TranscriptionConfig(sentiment_analysis=True)

        transcript = self.transcriber.transcribe(file_url, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"Error analyzing sentiment for {file_url}: {transcript.error}")
            return

        # Print sentiment analysis results
        print(f"\nSentiment Analysis for {file_url}:")
        for sentiment_result in transcript.sentiment_analysis:
            print(f"Text: {sentiment_result.text}")
            print(f"Sentiment: {sentiment_result.sentiment}")  # POSITIVE, NEUTRAL, or NEGATIVE
            print(f"Confidence: {sentiment_result.confidence}")
            print(f"Timestamp: {sentiment_result.start} - {sentiment_result.end}")


class ProcessAudio:
    def __init__(self, text: str, url: str, source_id: int, source_contents: list) -> None:
        self.text = text
        self.url = url
        self.source_id = source_id
        self.source_contents = source_contents

    async def process_text(self):
        analyzer = ContentAnalyzer()

        # Extract title and body from the transcription
        title, body = analyzer.extract_title_and_body(self.text)
        
        # Determine the type of the content at the URL
        url_type = analyzer.determine_url_type(self.url)

        # Create a new Content entry
        new_content = ContentCreate(
            source_id = self.source_id,
            title=title,
            body=body,
            url=self.url,
            type=url_type
        )

        # Save the content to the database  
        created_item = await create_item(new_content)
        if created_item is not None:
            logger.success(f"item created sucessfully: {created_item, self.source_id}")


async def main():
    async for batch in get_sources_in_batch(10, field="type", value="Audio"):
        batch = [{**record.__dict__} for record in batch]

        for item in batch:
            """Get all the children ids of each source in the batch"""
            ids = await get_source_item_ids(item['id'])

            """Process the audio based on the source url"""
            api_key = os.getenv("API_KEY")
            assembly_ai = AssemblyAIHelper(api_key=api_key)
            transcription_text = assembly_ai.transcribe(item['url'])

            if not transcription_text:
                logger.error(f"Transcription failed for {item['url']}")
                return
            else:
                """Process the trnascribed text"""
                audio = ProcessAudio(
                    text = transcription_text, 
                    url = item['url'], 
                    source_id = item['id'], 
                    source_contents = ids
                )
                await audio.process_text()


if __name__ == '__main__':
    asyncio.run(main())

