
import spacy
import requests

class ContentAnalyzer:
    def __init__(self):
        # Load the spaCy model for advanced NLP tasks
        self.nlp = spacy.load("en_core_web_sm")

    def extract_title_and_body(self, transcription: str) -> tuple:
        """
        Extracts a suitable title and body from the transcribed text using spaCy NLP.
        """
        # Process the transcription with spaCy
        doc = self.nlp(transcription)

        # Attempt to determine a title using the first sentence or noun chunks
        sentences = list(doc.sents)
        if sentences:
            title = sentences[0].text.strip()
        else:
            title = "Untitled"

        # Alternatively, extract a title based on noun chunks or entities
        if not title or len(title) < 5:  # Arbitrary length check for quality title
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            title = noun_chunks[0].strip() if noun_chunks else "Untitled"

        # The body is considered as the entire transcription minus the title
        body = transcription.strip()

        return title, body

    def determine_url_type(self, url: str) -> str:
        """
        Determines the type of the URL by checking the MIME type of the content.
        
        """
        response = requests.head(url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch the URL: {url}")
        
        content_type = response.headers.get('Content-Type', '')
        main_type = content_type.split('/')[0]
        
        if main_type in ['text', 'audio', 'video']:
            return main_type.capitalize()
        
        return None
