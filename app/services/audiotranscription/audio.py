import os, sys, asyncio

from dotenv import load_dotenv
from loguru import logger
import assemblyai as aai
from .extraction import ContentAnalyzer
from app.schemas.source import Source

current_dir = os.getcwd()
sys.path.append(current_dir)

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
            print(
                f"Sentiment: {sentiment_result.sentiment}"
            )  # POSITIVE, NEUTRAL, or NEGATIVE
            print(f"Confidence: {sentiment_result.confidence}")
            print(f"Timestamp: {sentiment_result.start} - {sentiment_result.end}")


class ProcessAudio:
    def __init__(self, text: str, url: str, source_id: int) -> None:
        self.text = text
        self.url = url
        self.source_id = source_id

    async def process_text(self):
        analyzer = ContentAnalyzer()

        # Extract title and body from the transcription
        title, body = analyzer.extract_title_and_body(self.text)

        # Determine the type of the content at the URL
        url_type = analyzer.determine_url_type(self.url)

        new_content = {
            "source_id": self.source_id,
            "title": title,
            "body": body,
            "url": self.url,
            "type": url_type,
            "image_url": None,
        }
        return new_content


async def main(source: Source):
    """Process the audio based on the source url"""
    api_key = os.getenv("API_KEY")
    assembly_ai = AssemblyAIHelper(api_key=api_key)
    transcription_text = assembly_ai.transcribe(source["url"])

    if not transcription_text:
        logger.error(f"Transcription failed for {source['url']}")
        return
    else:
        """Process the transcribed text"""
        audio = ProcessAudio(
            text=transcription_text, url=source["url"], source_id=source["id"]
        )
        return await audio.process_text()
