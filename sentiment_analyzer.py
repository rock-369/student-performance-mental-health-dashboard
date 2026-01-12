"""
NLP Sentiment Analysis Module
Analyzes student text feedback to detect emotional state
"""
from textblob import TextBlob
from typing import Dict, Any, List
import re


class SentimentAnalyzer:
    """
    Sentiment analysis for student feedback using TextBlob
    Classifies text as Positive, Neutral, or Negative
    """
    
    # Keywords that indicate stress or concern
    STRESS_KEYWORDS = [
        'stressed', 'anxious', 'worried', 'overwhelmed', 'struggling',
        'difficult', 'hard', 'failing', 'depressed', 'hopeless',
        'scared', 'confused', 'lost', 'behind', 'pressure',
        'tired', 'exhausted', 'burnout', 'frustrated', 'discouraged',
        'dropout', 'quit', 'hate', 'terrible', 'worst'
    ]
    
    # Keywords that indicate positive mental state
    POSITIVE_KEYWORDS = [
        'happy', 'excited', 'confident', 'motivated', 'accomplished',
        'great', 'excellent', 'love', 'enjoy', 'fantastic',
        'proud', 'satisfied', 'optimistic', 'wonderful', 'amazing',
        'successful', 'achieved', 'grateful', 'positive', 'engaged'
    ]
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of given text
        Returns: sentiment label, polarity, subjectivity, and detailed analysis
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': 'Neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'stress_indicators': [],
                'positive_indicators': [],
                'confidence': 0.5
            }
        
        # Check cache
        cache_key = hash(text)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # TextBlob analysis
        blob = TextBlob(cleaned_text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Find stress and positive indicators
        stress_found = self._find_keywords(cleaned_text, self.STRESS_KEYWORDS)
        positive_found = self._find_keywords(cleaned_text, self.POSITIVE_KEYWORDS)
        
        # Determine sentiment with keyword boosting
        sentiment, confidence = self._determine_sentiment(
            polarity, stress_found, positive_found
        )
        
        result = {
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'stress_indicators': stress_found,
            'positive_indicators': positive_found,
            'confidence': round(confidence, 3)
        }
        
        # Cache result
        self.analysis_cache[cache_key] = result
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _find_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find matching keywords in text"""
        found = []
        for keyword in keywords:
            if keyword in text:
                found.append(keyword)
        return found
    
    def _determine_sentiment(
        self, 
        polarity: float, 
        stress_keywords: List[str], 
        positive_keywords: List[str]
    ) -> tuple:
        """
        Determine final sentiment considering both TextBlob polarity and keywords
        Returns: (sentiment_label, confidence)
        """
        # Calculate keyword scores
        stress_score = len(stress_keywords) * 0.15
        positive_score = len(positive_keywords) * 0.15
        
        # Adjust polarity with keyword influence
        adjusted_polarity = polarity - stress_score + positive_score
        
        # Clamp to [-1, 1]
        adjusted_polarity = max(-1, min(1, adjusted_polarity))
        
        # Determine sentiment
        if adjusted_polarity > 0.1:
            sentiment = 'Positive'
            confidence = min(0.9, 0.5 + abs(adjusted_polarity) * 0.4)
        elif adjusted_polarity < -0.1:
            sentiment = 'Negative'
            confidence = min(0.9, 0.5 + abs(adjusted_polarity) * 0.4)
        else:
            sentiment = 'Neutral'
            confidence = 0.5 + (0.1 - abs(adjusted_polarity)) * 2
        
        # Boost confidence if keywords strongly support the sentiment
        if sentiment == 'Negative' and len(stress_keywords) >= 2:
            confidence = min(0.95, confidence + 0.1)
        if sentiment == 'Positive' and len(positive_keywords) >= 2:
            confidence = min(0.95, confidence + 0.1)
        
        return sentiment, confidence
    
    def analyze_batch(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple texts and return aggregate statistics
        """
        results = [self.analyze(text) for text in texts]
        
        positive_count = sum(1 for r in results if r['sentiment'] == 'Positive')
        neutral_count = sum(1 for r in results if r['sentiment'] == 'Neutral')
        negative_count = sum(1 for r in results if r['sentiment'] == 'Negative')
        
        avg_polarity = sum(r['polarity'] for r in results) / len(results) if results else 0
        
        all_stress = []
        all_positive = []
        for r in results:
            all_stress.extend(r['stress_indicators'])
            all_positive.extend(r['positive_indicators'])
        
        return {
            'total_analyzed': len(results),
            'sentiment_distribution': {
                'Positive': positive_count,
                'Neutral': neutral_count,
                'Negative': negative_count
            },
            'average_polarity': round(avg_polarity, 3),
            'common_stress_indicators': list(set(all_stress)),
            'common_positive_indicators': list(set(all_positive)),
            'individual_results': results
        }
    
    def get_mental_health_score(self, analysis_result: Dict[str, Any]) -> int:
        """
        Convert sentiment analysis to a mental health score (1-10)
        1 = Very concerning, 10 = Excellent
        """
        polarity = analysis_result['polarity']
        stress_count = len(analysis_result['stress_indicators'])
        positive_count = len(analysis_result['positive_indicators'])
        
        # Base score from polarity (maps -1,1 to 3,8)
        base_score = 5.5 + (polarity * 2.5)
        
        # Adjust for keywords
        base_score -= stress_count * 0.5
        base_score += positive_count * 0.3
        
        # Clamp to 1-10
        return max(1, min(10, round(base_score)))
