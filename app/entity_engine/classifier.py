import re
import string
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import requests
from transformers import pipeline
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection
DetectorFactory.seed = 0

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

class MultilingualNewsClassifier:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        
        # Load stopwords for both languages
        try:
            self.stop_words_en = set(stopwords.words('english'))
            self.stop_words_fr = set(stopwords.words('french'))
        except:
            nltk.download('stopwords')
            self.stop_words_en = set(stopwords.words('english'))
            self.stop_words_fr = set(stopwords.words('french'))
        
        # Define keywords for each category in both languages
        self.category_keywords = {
            'crime': {
                'en': [
                    'arrest', 'police', 'murder', 'theft', 'robbery', 'burglary', 'assault', 
                    'investigation', 'suspect', 'criminal', 'court', 'trial', 'prison', 
                    'jail', 'violence', 'shooting', 'stabbing', 'fraud', 'scam', 'illegal',
                    'law enforcement', 'detective', 'crime scene', 'victim', 'witness',
                    'prosecutor', 'defendant', 'guilty', 'innocent', 'sentence', 'conviction',
                    'drug', 'weapon', 'gang', 'vandalism', 'kidnapping', 'homicide'
                ],
                'fr': [
                    'arrestation', 'police', 'meurtre', 'vol', 'cambriolage', 'agression',
                    'enquête', 'suspect', 'criminel', 'tribunal', 'procès', 'prison',
                    'violence', 'fusillage', 'fraude', 'arnaque', 'illégal', 'gendarmerie',
                    'détective', 'victime', 'témoin', 'procureur', 'accusé', 'coupable',
                    'innocent', 'condamnation', 'drogue', 'arme', 'gang', 'vandalisme',
                    'enlèvement', 'homicide', 'délit', 'crime', 'justice', 'commissariat'
                ]
            },
            'education': {
                'en': [
                    'school', 'university', 'college', 'student', 'teacher', 'professor',
                    'education', 'learning', 'curriculum', 'exam', 'test', 'grade',
                    'academic', 'scholarship', 'graduation', 'degree', 'diploma',
                    'classroom', 'campus', 'tuition', 'enrollment', 'admission',
                    'faculty', 'principal', 'superintendent', 'educational', 'study',
                    'elementary', 'secondary', 'higher education', 'research'
                ],
                'fr': [
                    'école', 'université', 'collège', 'étudiant', 'professeur', 'enseignant',
                    'éducation', 'apprentissage', 'programme', 'examen', 'test', 'note',
                    'académique', 'bourse', 'diplôme', 'classe', 'campus', 'frais',
                    'inscription', 'admission', 'faculté', 'directeur', 'éducatif',
                    'étude', 'primaire', 'secondaire', 'supérieur', 'recherche',
                    'lycée', 'formation', 'cours', 'élève', 'scolarité'
                ]
            },
            'health': {
                'en': [
                    'hospital', 'doctor', 'patient', 'medical', 'medicine', 'treatment',
                    'disease', 'virus', 'infection', 'healthcare', 'health', 'clinic',
                    'surgery', 'therapy', 'vaccine', 'medication', 'prescription',
                    'diagnosis', 'symptom', 'epidemic', 'pandemic', 'nurse',
                    'physician', 'pharmaceutical', 'mental health', 'wellness',
                    'fitness', 'nutrition', 'diet', 'exercise', 'outbreak'
                ],
                'fr': [
                    'hôpital', 'docteur', 'médecin', 'patient', 'médical', 'médicament',
                    'traitement', 'maladie', 'virus', 'infection', 'santé', 'clinique',
                    'chirurgie', 'thérapie', 'vaccin', 'ordonnance', 'diagnostic',
                    'symptôme', 'épidémie', 'pandémie', 'infirmier', 'pharmaceutique',
                    'santé mentale', 'bien-être', 'nutrition', 'régime', 'exercice',
                    'urgence', 'soins', 'épidémie', 'prévention'
                ]
            },
            'politics': {
                'en': [
                    'government', 'president', 'minister', 'parliament', 'congress',
                    'election', 'vote', 'policy', 'law', 'legislation', 'political',
                    'politician', 'campaign', 'democracy', 'republican', 'democrat',
                    'party', 'senate', 'house', 'mayor', 'governor', 'state',
                    'federal', 'local government', 'administration', 'cabinet'
                ],
                'fr': [
                    'gouvernement', 'président', 'ministre', 'parlement', 'assemblée',
                    'élection', 'vote', 'politique', 'loi', 'législation', 'politique',
                    'politicien', 'campagne', 'démocratie', 'parti', 'sénat',
                    'maire', 'gouverneur', 'état', 'fédéral', 'administration',
                    'cabinet', 'député', 'conseil', 'municipal', 'régional'
                ]
            },
            'business': {
                'en': [
                    'company', 'business', 'economy', 'market', 'stock', 'investment',
                    'finance', 'money', 'profit', 'revenue', 'sales', 'trade',
                    'commerce', 'industry', 'corporate', 'entrepreneur', 'startup',
                    'merger', 'acquisition', 'bankruptcy', 'inflation', 'recession',
                    'growth', 'economic', 'financial', 'banking', 'loan'
                ],
                'fr': [
                    'entreprise', 'affaires', 'économie', 'marché', 'action', 'investissement',
                    'finance', 'argent', 'profit', 'revenus', 'ventes', 'commerce',
                    'industrie', 'entrepreneur', 'fusion', 'acquisition', 'faillite',
                    'inflation', 'récession', 'croissance', 'économique', 'financier',
                    'banque', 'prêt', 'société', 'bourse', 'emploi'
                ]
            },
            'technology': {
                'en': [
                    'technology', 'tech', 'computer', 'software', 'hardware', 'internet',
                    'digital', 'online', 'app', 'application', 'website', 'cyber',
                    'data', 'artificial intelligence', 'ai', 'machine learning',
                    'robot', 'automation', 'innovation', 'startup', 'silicon valley',
                    'programming', 'coding', 'developer', 'smartphone', 'tablet'
                ],
                'fr': [
                    'technologie', 'tech', 'ordinateur', 'logiciel', 'matériel', 'internet',
                    'numérique', 'en ligne', 'application', 'site web', 'cyber',
                    'données', 'intelligence artificielle', 'ia', 'apprentissage automatique',
                    'robot', 'automatisation', 'innovation', 'programmation',
                    'développeur', 'smartphone', 'tablette', 'informatique'
                ]
            },
            'sports': {
                'en': [
                    'football', 'basketball', 'soccer', 'baseball', 'tennis', 'golf',
                    'olympics', 'championship', 'tournament', 'league', 'team',
                    'player', 'athlete', 'coach', 'game', 'match', 'score',
                    'win', 'lose', 'victory', 'defeat', 'competition', 'sport',
                    'stadium', 'arena', 'training', 'fitness'
                ],
                'fr': [
                    'football', 'basketball', 'tennis', 'golf', 'olympiques',
                    'championnat', 'tournoi', 'ligue', 'équipe', 'joueur',
                    'athlète', 'entraîneur', 'match', 'score', 'victoire',
                    'défaite', 'compétition', 'sport', 'stade', 'entraînement',
                    'rugby', 'cyclisme', 'natation', 'athlétisme'
                ]
            }
        }
        
        # Initialize transformer model for zero-shot classification (optional)
        try:
            self.classifier = pipeline("zero-shot-classification", 
                                     model="facebook/bart-large-mnli")
        except:
            self.classifier = None
            print("Transformer model not available. Using keyword-based classification only.")
    
    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            detected_lang = detect(text)
            # Map detected language to our supported languages
            if detected_lang in ['en', 'fr']:
                return detected_lang
            else:
                # Default to English if language not supported
                return 'en'
        except LangDetectException:
            # If detection fails, try to guess based on common words
            text_lower = text.lower()
            french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'à', 'dans', 'pour', 'sur', 'avec', 'par', 'une', 'un']
            english_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an']
            
            french_count = sum(1 for word in french_indicators if word in text_lower)
            english_count = sum(1 for word in english_indicators if word in text_lower)
            
            return 'fr' if french_count > english_count else 'en'
    
    def preprocess_text(self, text, language):
        """Clean and preprocess the text based on language"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords based on language
        if language == 'fr':
            stop_words = self.stop_words_fr
        else:
            stop_words = self.stop_words_en
        
        # Remove stopwords and short words
        tokens = [token for token in tokens 
                 if token not in stop_words and len(token) > 2]
        
        # For English, apply lemmatization
        if language == 'en':
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def keyword_based_classification(self, text, language):
        """Classify text based on keyword matching"""
        tokens = self.preprocess_text(text, language)
        text_lower = text.lower()
        
        category_scores = {}
        
        for category, lang_keywords in self.category_keywords.items():
            keywords = lang_keywords.get(language, [])
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
        Classify news text into categories with language detection
        
        Args:
            text (str): News article text
            method (str): 'keyword', 'transformer', or 'hybrid'
        
        Returns:
            dict: Classification results including detected language
        """
        # Detect language first
        detected_language = self.detect_language(text)
        
        results = {
            'detected_language': detected_language,
            'text_preview': text[:100] + '...' if len(text) > 100 else text
        }
        
        if method in ['keyword', 'hybrid']:
            keyword_category, keyword_score = self.keyword_based_classification(text, detected_language)
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
    
    def add_custom_keywords(self, category, language, keywords):
        """Add custom keywords to a category for a specific language"""
        if category not in self.category_keywords:
            self.category_keywords[category] = {'en': [], 'fr': []}
        
        if language not in self.category_keywords[category]:
            self.category_keywords[category][language] = []
        
        self.category_keywords[category][language].extend(keywords)
    
    def create_new_category(self, category_name, keywords_en, keywords_fr):
        """Create a new category with keywords in both languages"""
        self.category_keywords[category_name] = {
            'en': keywords_en,
            'fr': keywords_fr
        }
    
    def get_language_stats(self, news_list):
        """Get statistics about languages in the news list"""
        language_count = {'en': 0, 'fr': 0, 'other': 0}
        
        for news_text in news_list:
            lang = self.detect_language(news_text)
            if lang in language_count:
                language_count[lang] += 1
            else:
                language_count['other'] += 1
        
        return language_count
    

def test_classifier():
    # Initialize multilingual classifier (en and fr)
    category_classifer = MultilingualNewsClassifier()
    
    sample_news = [
        "Police arrested two suspects in connection with the bank robbery that occurred yesterday in downtown. The investigation is ongoing.",
        "La police a arrêté deux suspects en relation avec le vol de banque qui a eu lieu hier au centre-ville. L'enquête se poursuit.",
        "The local university announced new scholarship programs for students pursuing engineering degrees. The program will benefit over 500 students.",
        "L'université locale a annoncé de nouveaux programmes de bourses pour les étudiants poursuivant des diplômes d'ingénierie.",
        "Health officials reported a new outbreak of flu in the region. Hospitals are preparing for increased patient admissions.",
        "Les responsables de la santé ont signalé une nouvelle épidémie de grippe dans la région. Les hôpitaux se préparent à une augmentation des admissions."
    ]
    
    # Get language statistics
    lang_stats = category_classifer.get_language_stats(sample_news)
    print("Language Distribution:")
    for lang, count in lang_stats.items():
        print(f"  {lang}: {count} articles")
    
    # Classify each article
    print("\n" + "="*50)
    for i, article in enumerate(sample_news, 1):
        print(f"\n--- Article {i} ---")
        print(f"Text: {article[:80]}...")
        
        result = category_classifer.classify_news(article, method='hybrid')
        print(f"Detected Language: {result['detected_language']}")
        print(f"Final Category: {result['final_category']}")
        
        if 'keyword' in result:
            print(f"Keyword-based: {result['keyword']['category']} (score: {result['keyword']['confidence']})")
        
        if 'transformer' in result:
            print(f"Transformer-based: {result['transformer']['category']} (confidence: {result['transformer']['confidence']:.2f})")
    
    # Add custom keywords example
    category_classifer.add_custom_keywords('crime', 'en', ['vandalism', 'shoplifting'])
    category_classifer.add_custom_keywords('crime', 'fr', ['vandalisme', 'vol à l\'étalage'])
    
    # Create new category example
    category_classifer.create_new_category('environment', 
                                 ['climate', 'pollution', 'recycling', 'conservation'],
                                 ['climat', 'pollution', 'recyclage', 'conservation'])
    
    print("\n--- Testing with custom category ---")
    env_news_en = "Scientists warn about increasing pollution levels affecting climate change patterns."
    env_news_fr = "Les scientifiques mettent en garde contre l'augmentation des niveaux de pollution affectant les modèles de changement climatique."
    
    for news in [env_news_en, env_news_fr]:
        result = category_classifer.classify_news(news)
        print(f"Language: {result['detected_language']}, Category: {result['final_category']}")


def classifier(article: str):
    category_classifer = MultilingualNewsClassifier()
    result = category_classifer.classify_news(article, method='hybrid')
    
    return result["final_category"]

if __name__ == "__main__":
    # multilingual classifier (en and fr)
    test_classifier()