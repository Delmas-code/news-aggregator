import re
import string
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import requests
from transformers import pipeline

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NewsClassifier:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Define keywords for each category
        self.category_keywords = {
            'crime': [
                'arrest', 'police', 'murder', 'theft', 'robbery', 'burglary', 'assault', 
                'investigation', 'suspect', 'criminal', 'court', 'trial', 'prison', 
                'jail', 'violence', 'shooting', 'stabbing', 'fraud', 'scam', 'illegal',
                'law enforcement', 'detective', 'crime scene', 'victim', 'witness',
                'prosecutor', 'defendant', 'guilty', 'innocent', 'sentence', 'conviction'
            ],
            'education': [
                'school', 'university', 'college', 'student', 'teacher', 'professor',
                'education', 'learning', 'curriculum', 'exam', 'test', 'grade',
                'academic', 'scholarship', 'graduation', 'degree', 'diploma',
                'classroom', 'campus', 'tuition', 'enrollment', 'admission',
                'faculty', 'principal', 'superintendent', 'educational', 'study'
            ],
            'health': [
                'hospital', 'doctor', 'patient', 'medical', 'medicine', 'treatment',
                'disease', 'virus', 'infection', 'healthcare', 'health', 'clinic',
                'surgery', 'therapy', 'vaccine', 'medication', 'prescription',
                'diagnosis', 'symptom', 'epidemic', 'pandemic', 'nurse',
                'physician', 'pharmaceutical', 'mental health', 'wellness',
                'fitness', 'nutrition', 'diet', 'exercise'
            ],
            'politics': [
                'government', 'president', 'minister', 'parliament', 'congress',
                'election', 'vote', 'policy', 'law', 'legislation', 'political',
                'politician', 'campaign', 'democracy', 'republican', 'democrat',
                'party', 'senate', 'house', 'mayor', 'governor', 'state',
                'federal', 'local government', 'administration', 'cabinet'
            ],
            'business': [
                'company', 'business', 'economy', 'market', 'stock', 'investment',
                'finance', 'money', 'profit', 'revenue', 'sales', 'trade',
                'commerce', 'industry', 'corporate', 'entrepreneur', 'startup',
                'merger', 'acquisition', 'bankruptcy', 'inflation', 'recession',
                'growth', 'economic', 'financial', 'banking', 'loan'
            ],
            'technology': [
                'technology', 'tech', 'computer', 'software', 'hardware', 'internet',
                'digital', 'online', 'app', 'application', 'website', 'cyber',
                'data', 'artificial intelligence', 'ai', 'machine learning',
                'robot', 'automation', 'innovation', 'startup', 'silicon valley',
                'programming', 'coding', 'developer', 'smartphone', 'tablet'
            ],
            'sports': [
                'football', 'basketball', 'soccer', 'baseball', 'tennis', 'golf',
                'olympics', 'championship', 'tournament', 'league', 'team',
                'player', 'athlete', 'coach', 'game', 'match', 'score',
                'win', 'lose', 'victory', 'defeat', 'competition', 'sport',
                'stadium', 'arena', 'training', 'fitness'
            ]
        }
        
        # Initialize transformer model for zero-shot classification (optional)
        try:
            self.classifier = pipeline("zero-shot-classification", 
                                     model="facebook/bart-large-mnli")
        except:
            self.classifier = None
            print("Transformer model not available. Using keyword-based classification only.")
    
    def preprocess_text(self, text):
        """Clean and preprocess the text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return tokens
    
    def keyword_based_classification(self, text):
        """Classify text based on keyword matching"""
        tokens = self.preprocess_text(text)
        text_lower = text.lower()
        
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of keyword in text
                if ' ' in keyword:  # Multi-word keyword
                    score += text_lower.count(keyword.lower()) * 2
                else:  # Single word keyword
                    score += tokens.count(keyword.lower())
            
            category_scores[category] = score
        
        # Return the category with highest score
        if max(category_scores.values()) == 0:
            return 'other', 0
        
        best_category = max(category_scores, key=category_scores.get)
        return best_category, category_scores[best_category]
    
    def transformer_classification(self, text):
        """Use transformer model for zero-shot classification"""
        if self.classifier is None:
            return None, 0
        
        categories = list(self.category_keywords.keys())
        
        try:
            result = self.classifier(text, categories)
            return result['labels'][0], result['scores'][0]
        except:
            return None, 0
    
    def classify_news(self, text, method='hybrid'):
        """
        Classify news text into categories
        
        Args:
            text (str): News article text
            method (str): 'keyword', 'transformer', or 'hybrid'
        
        Returns:
            dict: Classification results
        """
        results = {}
        
        if method in ['keyword', 'hybrid']:
            keyword_category, keyword_score = self.keyword_based_classification(text)
            results['keyword'] = {
                'category': keyword_category,
                'confidence': keyword_score
            }
        
        if method in ['transformer', 'hybrid'] and self.classifier is not None:
            transformer_category, transformer_score = self.transformer_classification(text)
            results['transformer'] = {
                'category': transformer_category,
                'confidence': transformer_score
            }
        
        # For hybrid approach, combine results
        if method == 'hybrid' and 'transformer' in results:
            # Use transformer if confidence is high, otherwise use keyword
            if results['transformer']['confidence'] > 0.7:
                final_category = results['transformer']['category']
            else:
                final_category = results['keyword']['category']
        else:
            final_category = results.get('keyword', {}).get('category', 'other')
        
        results['final_category'] = final_category
        return results
    
    def classify_multiple_news(self, news_list, method='hybrid'):
        """Classify multiple news articles"""
        results = []
        
        for i, news_text in enumerate(news_list):
            print(f"Processing article {i+1}/{len(news_list)}")
            result = self.classify_news(news_text, method)
            results.append(result)
        
        return results
    
    def add_custom_keywords(self, category, keywords):
        """Add custom keywords to a category"""
        if category not in self.category_keywords:
            self.category_keywords[category] = []
        
        self.category_keywords[category].extend(keywords)
    
    def create_new_category(self, category_name, keywords):
        """Create a new category with keywords"""
        self.category_keywords[category_name] = keywords

# Example usage
if __name__ == "__main__":
    # Initialize classifier
    classifier = NewsClassifier()
    
    # Sample news articles
    sample_news = [
        "Police arrested two suspects in connection with the bank robbery that occurred yesterday in downtown. The investigation is ongoing.",
        "The local university announced new scholarship programs for students pursuing engineering degrees. The program will benefit over 500 students.",
        "Health officials reported a new outbreak of flu in the region. Hospitals are preparing for increased patient admissions.",
        "The tech giant announced record quarterly profits driven by strong smartphone sales and cloud computing services.",
        "The basketball team won their championship game last night with a score of 95-87 in overtime."
    ]
    
    # Classify each article
    for i, article in enumerate(sample_news, 1):
        print(f"\n--- Article {i} ---")
        print(f"Text: {article[:100]}...")
        
        result = classifier.classify_news(article, method='hybrid')
        print(f"Final Category: {result['final_category']}")
        
        if 'keyword' in result:
            print(f"Keyword-based: {result['keyword']['category']} (score: {result['keyword']['confidence']})")
        
        if 'transformer' in result:
            print(f"Transformer-based: {result['transformer']['category']} (confidence: {result['transformer']['confidence']:.2f})")
    
    # Add custom keywords example
    classifier.add_custom_keywords('crime', ['vandalism', 'shoplifting', 'domestic violence'])
    
    # Create new category example
    classifier.create_new_category('environment', ['climate', 'pollution', 'recycling', 'conservation', 'renewable energy'])
    
    print("\n--- Testing with custom category ---")
    environmental_news = "Scientists warn about increasing pollution levels affecting climate change patterns."
    result = classifier.classify_news(environmental_news)
    print(f"Environmental news classified as: {result['final_category']}")