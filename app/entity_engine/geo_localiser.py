import spacy
from collections import Counter, defaultdict
import re
import requests
import time
import news_samples
from typing import Dict, Any, List, Optional



class LocationGeocoder:
    """
    Handles geocoding of locations using multiple services
    """
    def __init__(self, user_agent="EventLocationAnalyzer/1.0"):
        self.user_agent = user_agent
        self.cache = {}  # Simple in-memory cache
        self.rate_limit_delay = 2  # Seconds between requests
       
    def get_coordinates_nominatim(self, location_name: str) -> Optional[Dict]:
        """
        Get coordinates using OpenStreetMap Nominatim (free, no API key needed)
        """
        if location_name in self.cache:
            return self.cache[location_name]
       
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location_name,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1,
            'extratags': 1,
            'namedetails': 1
        }
       
        headers = {
            'User-Agent': self.user_agent
        }
       
        try:
            time.sleep(self.rate_limit_delay)  # Respect rate limits
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
           
            data = response.json()
            if data:
                result = self._parse_nominatim_response(data[0])
                self.cache[location_name] = result
                return result
           
        except Exception as e:
            print(f"Error geocoding {location_name} with Nominatim: {e}")
       
        return None
   
    def get_coordinates_geonames(self, location_name: str, username: str = None) -> Optional[Dict]:
        """
        Get coordinates using GeoNames API (requires free username)
        Sign up at: http://www.geonames.org/login
        """
        if not username:
            return None
           
        if location_name in self.cache:
            return self.cache[location_name]
       
        base_url = "http://api.geonames.org/searchJSON"
        params = {
            'q': location_name,
            'maxRows': 1,
            'username': username,
            'style': 'full'
        }
       
        try:
            time.sleep(0.1)  # Respect rate limits
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
           
            data = response.json()
            if 'geonames' in data and data['geonames']:
                result = self._parse_geonames_response(data['geonames'][0])
                self.cache[location_name] = result
                return result
               
        except Exception as e:
            print(f"Error geocoding {location_name} with GeoNames: {e}")
       
        return None
   
    def _parse_nominatim_response(self, data: Dict) -> Dict:
        """Parse Nominatim API response"""
        lat = float(data['lat'])
        lon = float(data['lon'])
       
        # Parse bounding box
        bbox = data.get('boundingbox', [])
        if len(bbox) == 4:
            # Nominatim returns [min_lat, max_lat, min_lon, max_lon]
            bounding_box = {
                'min_lat': float(bbox[0]),
                'max_lat': float(bbox[1]),
                'min_lon': float(bbox[2]),
                'max_lon': float(bbox[3])
            }
        else:
            # Create approximate bounding box (±0.01 degrees ≈ ±1.1km)
            bounding_box = {
                'min_lat': lat - 0.01,
                'max_lat': lat + 0.01,
                'min_lon': lon - 0.01,
                'max_lon': lon + 0.01
            }
       
        return {
            'centroid': {'lat': lat, 'lon': lon},
            'bounding_box': bounding_box,
            'display_name': data.get('display_name', ''),
            'place_type': data.get('type', ''),
            'country': data.get('address', {}).get('country', ''),
            'state': data.get('address', {}).get('state', ''),
            'city': data.get('address', {}).get('city', ''),
            'source': 'nominatim'
        }
   
    def _parse_geonames_response(self, data: Dict) -> Dict:
        """Parse GeoNames API response"""
        lat = float(data['lat'])
        lon = float(data['lng'])
       
        # GeoNames doesn't always provide bounding box, create approximate one
        bounding_box = {
            'min_lat': lat - 0.01,
            'max_lat': lat + 0.01,
            'min_lon': lon - 0.01,
            'max_lon': lon + 0.01
        }
       
        return {
            'centroid': {'lat': lat, 'lon': lon},
            'bounding_box': bounding_box,
            'display_name': data.get('toponymName', ''),
            'place_type': data.get('fclName', ''),
            'country': data.get('countryName', ''),
            'state': data.get('adminName1', ''),
            'city': data.get('name', ''),
            'population': data.get('population', 0),
            'source': 'geonames'
        }
   
    def geocode_location(self, location_name: str, geonames_username: str = None) -> Optional[Dict]:
        """
        Try to geocode a location using available services
        """
        # Try Nominatim first (free, no registration needed)
        result = self.get_coordinates_nominatim(location_name)
       
        # If Nominatim fails and GeoNames username is provided, try GeoNames
        if not result and geonames_username:
            result = self.get_coordinates_geonames(location_name, geonames_username)
       
        return result
    


class EventLocationPredictor:
    def __init__(self, model_name="en_core_web_trf"):
        self.nlp = spacy.load(model_name)
       
        # Keywords that indicate event occurrence
        self.event_indicators = {
            'happening': ['occurred', 'happened', 'took place', 'witnessed', 'reported', 'broke out'],
            'present_tense': ['is happening', 'are occurring', 'taking place', 'underway'],
            'location_prepositions': ['in', 'at', 'near', 'around', 'within', 'outside', 'inside']
        }
       
        # Entity type hierarchy (GPE > LOC > FAC for events)
        self.entity_priority = {'GPE': 3, 'LOC': 2, 'FAC': 1}
   
    def extract_locations_with_context(self, text):
        """Extract locations with their surrounding context and positions"""
        doc = self.nlp(text)
        locations = []
       
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:
                # Get sentence containing the entity
                sent = ent.sent
               
                # Get position in text (earlier = more important for news)
                position_ratio = ent.start_char / len(text)
               
                locations.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'sentence': sent.text,
                    'position_ratio': position_ratio,
                    'token_position': ent.start,
                    'doc': doc
                })
       
        return locations
   
    def calculate_location_scores(self, locations, text):
        """Calculate scores for each location based on multiple factors"""
        scores = defaultdict(float)
        location_data = {}
       
        for loc in locations:
            loc_text = loc['text'].lower()
            sentence = loc['sentence'].lower()
           
            # Initialize if not exists
            if loc_text not in location_data:
                location_data[loc_text] = {
                    'entity_type': loc['label'],
                    'occurrences': 0,
                    'contexts': [],
                    'positions': []
                }
           
            location_data[loc_text]['occurrences'] += 1
            location_data[loc_text]['contexts'].append(sentence)
            location_data[loc_text]['positions'].append(loc['position_ratio'])
           
            # Score based on entity type priority
            scores[loc_text] += self.entity_priority.get(loc['label'], 0)
           
            # Score based on proximity to event indicators
            context_score = self._score_context_relevance(sentence, loc_text)
            scores[loc_text] += context_score
           
            # Score based on position in text (earlier = more important)
            position_score = (1 - loc['position_ratio']) * 2  # Max 2 points
            scores[loc_text] += position_score
           
            # Score based on grammatical relationships
            grammar_score = self._score_grammatical_relationships(loc, text)
            scores[loc_text] += grammar_score
       
        # Frequency bonus (but cap it to avoid over-weighting)
        for loc_text, data in location_data.items():
            frequency_score = min(data['occurrences'] * 0.5, 2.0)  # Max 2 points
            scores[loc_text] += frequency_score
       
        return scores, location_data
   
    def _score_context_relevance(self, sentence, location):
        """Score based on proximity to event-indicating words"""
        score = 0
       
        # Check for event indicators in the same sentence
        for category, indicators in self.event_indicators.items():
            for indicator in indicators:
                if indicator in sentence:
                    if category == 'happening':
                        score += 3
                    elif category == 'present_tense':
                        score += 2
                    elif category == 'location_prepositions':
                        # Check if preposition is near the location
                        if self._is_preposition_near_location(sentence, location, indicator):
                            score += 4
       
        return score
   
    def _is_preposition_near_location(self, sentence, location, preposition):
        """Check if location preposition is directly before location"""
        # Simple pattern matching for "preposition + location"
        pattern = rf'\b{re.escape(preposition)}\s+\w*\s*{re.escape(location)}\b'
        return bool(re.search(pattern, sentence, re.IGNORECASE))
   
    def _score_grammatical_relationships(self, location_info, text):
        """Score based on grammatical relationships in the dependency tree"""
        score = 0
        doc = location_info['doc']
       
        # Find the location entity in the doc
        for ent in doc.ents:
            if (ent.start_char == location_info['start'] and
                ent.end_char == location_info['end']):
               
                # Check if location is subject or object of action verbs
                for token in ent:
                    if token.dep_ in ['pobj', 'dobj']:  # Object of preposition/verb
                        head = token.head
                        if head.pos_ == 'VERB':
                            score += 2
                    elif token.dep_ in ['nsubj', 'nsubjpass']:  # Subject
                        score += 1
               
                break
       
        return score
   
    def get_most_likely_event_location(self, news_article: Dict[str, Any], return_all_scores=False):
        """
        Get the most likely location where the event occurred
       
        Args:
            text: Input text to analyze
            return_all_scores: If True, return all locations with scores
           
        Returns:
            If return_all_scores=False: tuple (most_likely_location, confidence_score)
            If return_all_scores=True: dict with all locations and their scores
        """
        
        title = news_article.get("title", "")
        body = news_article.get("body", "")
        text = f"{title}. {body}"

        locations = self.extract_locations_with_context(text)
       
        if not locations:
            return False, None if not return_all_scores else {}
       
        scores, location_data = self.calculate_location_scores(locations, text)
       
        # Sort by score
        sorted_locations = sorted(scores.items(), key=lambda x: x[1], reverse=True)
       
        if return_all_scores:
            result = {}
            for loc, score in sorted_locations:
                result[loc] = {
                    'score': score,
                    'entity_type': location_data[loc]['entity_type'],
                    'occurrences': location_data[loc]['occurrences'],
                    'avg_position': sum(location_data[loc]['positions']) / len(location_data[loc]['positions'])
                }
            return True, result
        else:
            if sorted_locations:
                best_location, best_score = sorted_locations[0]
                # Calculate confidence (normalized score)
                max_possible_score = 10  # Rough estimate of max possible score
                confidence = min(best_score / max_possible_score, 1.0)
                return True, [best_location, confidence]
            return False, None


def main_localiser(news_data =  None):
    loc_predictor = EventLocationPredictor()
    geo_cords = LocationGeocoder()

    if not news_data:
        for sample in news_samples.sample_news_article_list:
            news_data = {
                "id" : sample["id"],
                "title" : sample["title"],
                "body" : sample["body"],
                "url" : sample["url"],
                "type" : sample["type"],
                "tags" : sample["tags"]
            }
            # Get all locations with scores
            status, loc_result = loc_predictor.get_most_likely_event_location(sample)
            if status:
                location, confidence = loc_result[0], loc_result[1]
            else:
                location, confidence = None, None

            if not location:
                location_result = {}
                print(f'\n{location_result}\n')
                continue
            
            geo_result = geo_cords.geocode_location(f'{location}')
            geo_result["confidence"] = confidence
            location_result = geo_result
            print(f'\n{location_result}\n')
            
            return location_result
    
    # Get all locations with scores
    status, loc_result = loc_predictor.get_most_likely_event_location(news_data)
    if status:
        location, confidence = loc_result[0], loc_result[1]
    else:
        location, confidence = None, None

    if not location:
        location_result = None
        print(f'\n{location_result}\n')
        return location_result
    
    geo_result = geo_cords.geocode_location(f'{location}')
    geo_result["confidence"] = confidence
    location_result = geo_result
    print(f'\n{location_result}\n')
    
    return location_result
            
        
    # for i, text in enumerate(examples, 1):
    #     print(f"\nExample {i}:")
    #     print(f"Text: {text}")
       
    #     # Get most likely location
    #     result = predictor.get_most_likely_event_location(text)
    #     if result[0]:
    #         print(f"Most likely event location: {result[0]} (confidence: {result[1]:.2f})")
       
    #     # Get all locations with scores
    #     all_scores = predictor.get_most_likely_event_location(text, return_all_scores=True)
    #     print("All locations with scores:")
    #     for loc, data in all_scores.items():
    #         print(f"  {loc}: {data['score']:.1f} points ({data['entity_type']}, {data['occurrences']} occurrences)")

if __name__ == "__main__":
    main_localiser()
