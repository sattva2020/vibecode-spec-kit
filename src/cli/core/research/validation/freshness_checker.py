"""
Freshness checker for assessing content recency and relevance
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class FreshnessChecker:
    """Checker for assessing content freshness and recency"""
    
    def __init__(self):
        self.date_patterns = self._initialize_date_patterns()
        self.freshness_thresholds = self._initialize_freshness_thresholds()
        self.recency_indicators = self._initialize_recency_indicators()
    
    def _initialize_date_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize date extraction patterns"""
        return {
            'iso_date': {
                'pattern': r'(\d{4}-\d{2}-\d{2})',
                'format': '%Y-%m-%d',
                'priority': 1
            },
            'us_date': {
                'pattern': r'(\d{1,2}/\d{1,2}/\d{4})',
                'format': '%m/%d/%Y',
                'priority': 2
            },
            'european_date': {
                'pattern': r'(\d{1,2}/\d{1,2}/\d{4})',
                'format': '%d/%m/%Y',
                'priority': 3
            },
            'month_year': {
                'pattern': r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',
                'format': '%B %Y',
                'priority': 4
            },
            'abbreviated_month': {
                'pattern': r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})',
                'format': '%b %Y',
                'priority': 5
            },
            'year_only': {
                'pattern': r'(\d{4})',
                'format': '%Y',
                'priority': 6
            }
        }
    
    def _initialize_freshness_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize freshness assessment thresholds"""
        return {
            'very_fresh': {
                'max_age_days': 7,
                'score_range': (0.9, 1.0),
                'description': 'Very recent content (within a week)'
            },
            'fresh': {
                'max_age_days': 30,
                'score_range': (0.7, 0.9),
                'description': 'Recent content (within a month)'
            },
            'moderately_fresh': {
                'max_age_days': 90,
                'score_range': (0.5, 0.7),
                'description': 'Moderately recent content (within 3 months)'
            },
            'stale': {
                'max_age_days': 365,
                'score_range': (0.3, 0.5),
                'description': 'Stale content (within a year)'
            },
            'very_stale': {
                'max_age_days': float('inf'),
                'score_range': (0.0, 0.3),
                'description': 'Very stale content (over a year old)'
            }
        }
    
    def _initialize_recency_indicators(self) -> Dict[str, List[str]]:
        """Initialize recency indicator keywords"""
        return {
            'very_recent': [
                'today', 'yesterday', 'this week', 'recently', 'just released',
                'latest', 'newest', 'current', 'up to date', 'fresh'
            ],
            'recent': [
                'this month', 'last month', 'recently updated', 'latest version',
                'new', 'updated', 'current', 'modern', 'contemporary'
            ],
            'moderate': [
                'this year', 'last year', 'recent', 'updated', 'version',
                'release', 'published', 'announced'
            ],
            'old': [
                'legacy', 'deprecated', 'outdated', 'obsolete', 'old version',
                'previous', 'former', 'historical', 'archived'
            ]
        }
    
    def check_freshness(self, 
                       content: str, 
                       url: str = "", 
                       title: str = "",
                       accessed_at: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Check content freshness and recency
        
        Args:
            content: Content to check
            url: Source URL (may contain date indicators)
            title: Content title (may contain date indicators)
            accessed_at: When the content was accessed
        
        Returns:
            Freshness assessment results
        """
        freshness_result = {
            'freshness_score': 0.0,
            'age_category': 'unknown',
            'detected_dates': [],
            'confidence': 0.0,
            'recommendations': [],
            'details': {}
        }
        
        # Extract dates from various sources
        detected_dates = self._extract_dates(content, url, title)
        freshness_result['detected_dates'] = detected_dates
        
        # Calculate freshness score
        if detected_dates:
            freshness_result['freshness_score'] = self._calculate_freshness_score(detected_dates, accessed_at)
            freshness_result['age_category'] = self._categorize_age(freshness_result['freshness_score'])
        else:
            # Fallback to content analysis
            freshness_result['freshness_score'] = self._analyze_content_recency(content)
            freshness_result['age_category'] = self._categorize_age(freshness_result['freshness_score'])
        
        # Calculate confidence
        freshness_result['confidence'] = self._calculate_freshness_confidence(detected_dates, content)
        
        # Generate recommendations
        freshness_result['recommendations'] = self._generate_freshness_recommendations(freshness_result)
        
        # Add detailed analysis
        freshness_result['details'] = {
            'date_extraction_method': 'automatic' if detected_dates else 'content_analysis',
            'primary_date_source': self._identify_primary_date_source(detected_dates),
            'content_recency_indicators': self._find_recency_indicators(content),
            'url_date_indicators': self._extract_url_dates(url)
        }
        
        return freshness_result
    
    def _extract_dates(self, content: str, url: str = "", title: str = "") -> List[Dict[str, Any]]:
        """Extract dates from content, URL, and title"""
        all_dates = []
        
        # Extract from content
        content_dates = self._extract_dates_from_text(content)
        for date_info in content_dates:
            date_info['source'] = 'content'
            all_dates.append(date_info)
        
        # Extract from URL
        if url:
            url_dates = self._extract_dates_from_text(url)
            for date_info in url_dates:
                date_info['source'] = 'url'
                all_dates.append(date_info)
        
        # Extract from title
        if title:
            title_dates = self._extract_dates_from_text(title)
            for date_info in title_dates:
                date_info['source'] = 'title'
                all_dates.append(date_info)
        
        # Sort by priority and remove duplicates
        all_dates.sort(key=lambda x: (x['priority'], x['confidence']), reverse=True)
        
        # Remove duplicate dates
        unique_dates = []
        seen_dates = set()
        for date_info in all_dates:
            date_key = (date_info['date'], date_info['source'])
            if date_key not in seen_dates:
                unique_dates.append(date_info)
                seen_dates.add(date_key)
        
        return unique_dates
    
    def _extract_dates_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text using various patterns"""
        dates = []
        
        for pattern_name, pattern_info in self.date_patterns.items():
            pattern = pattern_info['pattern']
            format_str = pattern_info['format']
            priority = pattern_info['priority']
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if pattern_name in ['month_year', 'abbreviated_month']:
                        # Handle month name patterns
                        month_name = match.group(1).lower()
                        year = int(match.group(2))
                        
                        # Convert month name to number
                        month_map = {
                            'january': 1, 'jan': 1,
                            'february': 2, 'feb': 2,
                            'march': 3, 'mar': 3,
                            'april': 4, 'apr': 4,
                            'may': 5,
                            'june': 6, 'jun': 6,
                            'july': 7, 'jul': 7,
                            'august': 8, 'aug': 8,
                            'september': 9, 'sep': 9,
                            'october': 10, 'oct': 10,
                            'november': 11, 'nov': 11,
                            'december': 12, 'dec': 12
                        }
                        
                        month = month_map.get(month_name, 1)
                        date_obj = datetime(year, month, 1)
                        
                    elif pattern_name == 'year_only':
                        # Handle year-only patterns
                        year = int(match.group(1))
                        date_obj = datetime(year, 1, 1)
                        
                    else:
                        # Handle other date patterns
                        date_str = match.group(1)
                        date_obj = datetime.strptime(date_str, format_str)
                    
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_date_confidence(pattern_name, date_obj)
                    
                    dates.append({
                        'date': date_obj,
                        'date_string': match.group(0),
                        'pattern': pattern_name,
                        'priority': priority,
                        'confidence': confidence,
                        'position': match.start()
                    })
                    
                except ValueError:
                    # Skip invalid dates
                    continue
        
        return dates
    
    def _calculate_date_confidence(self, pattern_name: str, date_obj: datetime) -> float:
        """Calculate confidence in extracted date"""
        confidence_scores = {
            'iso_date': 0.95,
            'us_date': 0.90,
            'european_date': 0.85,
            'month_year': 0.80,
            'abbreviated_month': 0.75,
            'year_only': 0.60
        }
        
        base_confidence = confidence_scores.get(pattern_name, 0.5)
        
        # Adjust confidence based on date reasonableness
        current_year = datetime.now().year
        
        # Penalty for future dates
        if date_obj.year > current_year + 1:
            base_confidence *= 0.5
        
        # Penalty for very old dates (before 1990)
        if date_obj.year < 1990:
            base_confidence *= 0.7
        
        # Bonus for recent dates
        if date_obj.year >= current_year - 2:
            base_confidence *= 1.1
        
        return min(1.0, base_confidence)
    
    def _calculate_freshness_score(self, detected_dates: List[Dict[str, Any]], accessed_at: Optional[datetime] = None) -> float:
        """Calculate freshness score based on detected dates"""
        if not detected_dates:
            return 0.5  # Default score when no dates found
        
        # Use the most confident date
        best_date = max(detected_dates, key=lambda x: x['confidence'])
        date_obj = best_date['date']
        
        # Calculate age
        reference_date = accessed_at if accessed_at else datetime.now()
        age = reference_date - date_obj
        age_days = age.days
        
        # Calculate score based on age
        for category, thresholds in self.freshness_thresholds.items():
            if age_days <= thresholds['max_age_days']:
                min_score, max_score = thresholds['score_range']
                
                # Interpolate score within the range
                if thresholds['max_age_days'] == float('inf'):
                    # For very stale content, use minimum score
                    return min_score
                
                # Linear interpolation
                ratio = age_days / thresholds['max_age_days']
                score = max_score - (ratio * (max_score - min_score))
                
                # Apply confidence weighting
                confidence_weight = best_date['confidence']
                return score * confidence_weight + 0.5 * (1 - confidence_weight)
        
        return 0.0
    
    def _analyze_content_recency(self, content: str) -> float:
        """Analyze content for recency indicators when no dates are found"""
        content_lower = content.lower()
        score = 0.5  # Base score
        
        # Check for very recent indicators
        very_recent_count = sum(1 for indicator in self.recency_indicators['very_recent']
                               if indicator in content_lower)
        if very_recent_count > 0:
            score += 0.3
        
        # Check for recent indicators
        recent_count = sum(1 for indicator in self.recency_indicators['recent']
                          if indicator in content_lower)
        if recent_count > 0:
            score += 0.2
        
        # Check for moderate indicators
        moderate_count = sum(1 for indicator in self.recency_indicators['moderate']
                            if indicator in content_lower)
        if moderate_count > 0:
            score += 0.1
        
        # Check for old indicators (penalty)
        old_count = sum(1 for indicator in self.recency_indicators['old']
                       if indicator in content_lower)
        if old_count > 0:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _categorize_age(self, freshness_score: float) -> str:
        """Categorize content age based on freshness score"""
        if freshness_score >= 0.9:
            return 'very_fresh'
        elif freshness_score >= 0.7:
            return 'fresh'
        elif freshness_score >= 0.5:
            return 'moderately_fresh'
        elif freshness_score >= 0.3:
            return 'stale'
        else:
            return 'very_stale'
    
    def _calculate_freshness_confidence(self, detected_dates: List[Dict[str, Any]], content: str) -> float:
        """Calculate confidence in freshness assessment"""
        if not detected_dates:
            # Low confidence when no dates found
            return 0.3
        
        # Higher confidence with multiple date sources
        source_count = len(set(date['source'] for date in detected_dates))
        confidence = 0.4 + (source_count * 0.2)
        
        # Boost confidence with high-quality date patterns
        high_quality_dates = [d for d in detected_dates if d['pattern'] in ['iso_date', 'us_date']]
        if high_quality_dates:
            confidence += 0.2
        
        # Check for recency indicators in content
        recency_indicators = self._find_recency_indicators(content)
        if recency_indicators:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _find_recency_indicators(self, content: str) -> List[str]:
        """Find recency indicators in content"""
        content_lower = content.lower()
        found_indicators = []
        
        for category, indicators in self.recency_indicators.items():
            for indicator in indicators:
                if indicator in content_lower:
                    found_indicators.append(indicator)
        
        return found_indicators
    
    def _extract_url_dates(self, url: str) -> List[str]:
        """Extract date indicators from URL"""
        if not url:
            return []
        
        date_patterns = [
            r'/(\d{4})/',  # /2024/
            r'/(\d{4}-\d{2})/',  # /2024-01/
            r'/(\d{4}-\d{2}-\d{2})/',  # /2024-01-15/
        ]
        
        url_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, url)
            url_dates.extend(matches)
        
        return url_dates
    
    def _identify_primary_date_source(self, detected_dates: List[Dict[str, Any]]) -> str:
        """Identify the primary source of date information"""
        if not detected_dates:
            return 'none'
        
        # Prioritize by source reliability
        source_priority = {'url': 1, 'title': 2, 'content': 3}
        
        best_date = min(detected_dates, key=lambda x: source_priority.get(x['source'], 4))
        return best_date['source']
    
    def _generate_freshness_recommendations(self, freshness_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on freshness assessment"""
        recommendations = []
        
        freshness_score = freshness_result['freshness_score']
        age_category = freshness_result['age_category']
        
        if age_category in ['stale', 'very_stale']:
            recommendations.append("Content is outdated, consider finding more recent sources")
        
        if freshness_result['confidence'] < 0.6:
            recommendations.append("Freshness assessment has low confidence, manual review recommended")
        
        if not freshness_result['detected_dates']:
            recommendations.append("No clear dates found, consider sources with explicit timestamps")
        
        if age_category == 'very_fresh':
            recommendations.append("Content is very recent, high confidence in freshness")
        
        return recommendations
