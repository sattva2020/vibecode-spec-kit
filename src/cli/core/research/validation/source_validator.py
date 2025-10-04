"""
Source validator for assessing source quality and credibility
"""

import re
import urllib.parse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..templates.research_template import Source


class SourceValidator:
    """Validator for research sources"""
    
    def __init__(self):
        self.credibility_domains = self._initialize_credibility_domains()
        self.url_patterns = self._initialize_url_patterns()
        self.content_quality_indicators = self._initialize_content_quality_indicators()
    
    def _initialize_credibility_domains(self) -> Dict[str, float]:
        """Initialize domain credibility scores"""
        return {
            # High credibility (0.9-1.0)
            'github.com': 0.95,
            'docs.python.org': 0.95,
            'developer.mozilla.org': 0.95,
            'nodejs.org': 0.95,
            'reactjs.org': 0.95,
            'vuejs.org': 0.95,
            'angular.io': 0.95,
            'kubernetes.io': 0.95,
            'apache.org': 0.95,
            'postgresql.org': 0.95,
            'python.org': 0.95,
            
            # Very high credibility (0.8-0.9)
            'stackoverflow.com': 0.90,
            'aws.amazon.com': 0.90,
            'cloud.google.com': 0.90,
            'azure.microsoft.com': 0.90,
            'docker.com': 0.90,
            'redis.io': 0.90,
            'mongodb.com': 0.90,
            'mysql.com': 0.90,
            'nginx.org': 0.90,
            'elastic.co': 0.90,
            'jenkins.io': 0.90,
            'gitlab.com': 0.90,
            'npmjs.com': 0.85,
            'pypi.org': 0.90,
            
            # High credibility (0.7-0.8)
            'medium.com': 0.70,
            'dev.to': 0.75,
            'hashnode.com': 0.70,
            'freecodecamp.org': 0.80,
            'codecademy.com': 0.75,
            'w3schools.com': 0.70,
            'geeksforgeeks.org': 0.75,
            'realpython.com': 0.80,
            'atlassian.com': 0.85,
            'slack.com': 0.85,
            
            # Medium credibility (0.5-0.7)
            'blogspot.com': 0.50,
            'wordpress.com': 0.55,
            'reddit.com': 0.60,
            'quora.com': 0.65,
            'youtube.com': 0.70,
            'slideshare.net': 0.60,
            
            # Low credibility (0.3-0.5)
            'tumblr.com': 0.40,
            'scribd.com': 0.55,
            'issuu.com': 0.50
        }
    
    def _initialize_url_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize URL pattern validation"""
        return {
            'valid_schemes': ['http', 'https'],
            'invalid_patterns': [
                r'\.(exe|zip|rar|tar|gz)$',
                r'\.(pdf|doc|docx)$',  # Document files
                r'\.(jpg|jpeg|png|gif|svg)$',  # Image files
                r'\.(mp4|avi|mov|wmv)$',  # Video files
                r'\.(mp3|wav|flac)$',  # Audio files
                r'/download/',
                r'/file/',
                r'/attachment/',
                r'/media/'
            ],
            'suspicious_patterns': [
                r'bit\.ly/',
                r'tinyurl\.com/',
                r'goo\.gl/',
                r'ow\.ly/',
                r't\.co/'
            ]
        }
    
    def _initialize_content_quality_indicators(self) -> Dict[str, List[str]]:
        """Initialize content quality indicators"""
        return {
            'positive_indicators': [
                'documentation', 'tutorial', 'guide', 'reference', 'api',
                'best practice', 'example', 'implementation', 'analysis',
                'framework', 'library', 'tool', 'methodology', 'approach'
            ],
            'negative_indicators': [
                'spam', 'advertisement', 'clickbait', 'fake', 'scam',
                'malware', 'virus', 'phishing', 'fraud', 'scam',
                'promotion', 'marketing', 'sales', 'buy now', 'limited time'
            ],
            'technical_indicators': [
                'code', 'function', 'class', 'method', 'algorithm',
                'database', 'server', 'client', 'api', 'endpoint',
                'configuration', 'installation', 'setup', 'deployment'
            ]
        }
    
    def validate_source(self, source: Source) -> Dict[str, Any]:
        """
        Validate a research source comprehensively
        
        Args:
            source: Source to validate
        
        Returns:
            Validation results with score and details
        """
        validation = {
            'score': 0.0,
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # URL validation
        url_validation = self._validate_url(source.url)
        validation['details']['url'] = url_validation
        if not url_validation['is_valid']:
            validation['errors'].extend(url_validation['errors'])
        
        # Domain validation
        domain_validation = self._validate_domain(source.domain)
        validation['details']['domain'] = domain_validation
        
        # Content validation
        content_validation = self._validate_content(source.content, source.title)
        validation['details']['content'] = content_validation
        
        # Credibility validation
        credibility_validation = self._validate_credibility(source)
        validation['details']['credibility'] = credibility_validation
        
        # Freshness validation
        freshness_validation = self._validate_freshness(source)
        validation['details']['freshness'] = freshness_validation
        
        # Calculate overall score
        validation['score'] = self._calculate_source_score(validation['details'])
        
        # Determine validity
        if validation['errors']:
            validation['is_valid'] = False
        
        # Generate warnings
        if validation['score'] < 0.6:
            validation['warnings'].append(f"Low quality source (score: {validation['score']:.2f})")
        
        return validation
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL format and patterns"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': 0.0
        }
        
        if not url:
            validation['errors'].append("URL is empty")
            validation['is_valid'] = False
            return validation
        
        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            validation['errors'].append(f"Invalid URL format: {e}")
            validation['is_valid'] = False
            return validation
        
        # Check scheme
        if parsed.scheme not in self.url_patterns['valid_schemes']:
            validation['errors'].append(f"Invalid URL scheme: {parsed.scheme}")
            validation['is_valid'] = False
        
        # Check for invalid patterns
        for pattern in self.url_patterns['invalid_patterns']:
            if re.search(pattern, url, re.IGNORECASE):
                validation['warnings'].append(f"URL matches invalid pattern: {pattern}")
        
        # Check for suspicious patterns
        for pattern in self.url_patterns['suspicious_patterns']:
            if re.search(pattern, url, re.IGNORECASE):
                validation['warnings'].append(f"URL uses suspicious shortener: {pattern}")
        
        # Calculate URL score
        score = 1.0
        score -= len(validation['errors']) * 0.3
        score -= len(validation['warnings']) * 0.1
        validation['score'] = max(0.0, score)
        
        return validation
    
    def _validate_domain(self, domain: str) -> Dict[str, Any]:
        """Validate domain credibility"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': 0.5,
            'credibility_score': 0.5
        }
        
        if not domain:
            validation['errors'].append("Domain is empty")
            validation['is_valid'] = False
            return validation
        
        # Get credibility score
        credibility_score = self.credibility_domains.get(domain, 0.5)
        validation['credibility_score'] = credibility_score
        validation['score'] = credibility_score
        
        # Add warnings for low credibility
        if credibility_score < 0.4:
            validation['warnings'].append(f"Low credibility domain: {domain}")
        elif credibility_score < 0.6:
            validation['warnings'].append(f"Medium credibility domain: {domain}")
        
        return validation
    
    def _validate_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """Validate content quality"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': 0.0
        }
        
        if not content:
            validation['errors'].append("Content is empty")
            validation['is_valid'] = False
            return validation
        
        combined_text = f"{title} {content}".lower()
        score = 0.5  # Base score
        
        # Check positive indicators
        positive_matches = sum(1 for indicator in self.content_quality_indicators['positive_indicators'] 
                              if indicator in combined_text)
        score += positive_matches * 0.05
        
        # Check negative indicators
        negative_matches = sum(1 for indicator in self.content_quality_indicators['negative_indicators'] 
                              if indicator in combined_text)
        score -= negative_matches * 0.1
        
        # Check technical indicators
        technical_matches = sum(1 for indicator in self.content_quality_indicators['technical_indicators'] 
                               if indicator in combined_text)
        score += technical_matches * 0.03
        
        # Content length check
        if len(content) < 100:
            validation['warnings'].append("Content is very short")
            score -= 0.2
        elif len(content) > 5000:
            score += 0.1  # Bonus for substantial content
        
        # Add warnings for low quality
        if negative_matches > 2:
            validation['warnings'].append("Content contains multiple negative quality indicators")
        
        validation['score'] = max(0.0, min(1.0, score))
        return validation
    
    def _validate_credibility(self, source: Source) -> Dict[str, Any]:
        """Validate source credibility"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': source.credibility_score
        }
        
        # Check credibility score range
        if source.credibility_score < 0.0 or source.credibility_score > 1.0:
            validation['errors'].append(f"Invalid credibility score: {source.credibility_score}")
            validation['is_valid'] = False
        
        # Add warnings for low credibility
        if source.credibility_score < 0.4:
            validation['warnings'].append("Very low credibility score")
        elif source.credibility_score < 0.6:
            validation['warnings'].append("Low credibility score")
        
        return validation
    
    def _validate_freshness(self, source: Source) -> Dict[str, Any]:
        """Validate source freshness"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': source.freshness_score
        }
        
        # Check freshness score range
        if source.freshness_score < 0.0 or source.freshness_score > 1.0:
            validation['errors'].append(f"Invalid freshness score: {source.freshness_score}")
            validation['is_valid'] = False
        
        # Check access time
        if source.accessed_at:
            time_since_access = datetime.now() - source.accessed_at
            
            if time_since_access > timedelta(days=30):
                validation['warnings'].append("Source accessed more than 30 days ago")
            elif time_since_access > timedelta(days=7):
                validation['warnings'].append("Source accessed more than 7 days ago")
        
        # Add warnings for low freshness
        if source.freshness_score < 0.4:
            validation['warnings'].append("Very low freshness score")
        elif source.freshness_score < 0.6:
            validation['warnings'].append("Low freshness score")
        
        return validation
    
    def _calculate_source_score(self, validation_details: Dict[str, Any]) -> float:
        """Calculate overall source validation score"""
        weights = {
            'url': 0.15,
            'domain': 0.25,
            'content': 0.25,
            'credibility': 0.20,
            'freshness': 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for component, weight in weights.items():
            if component in validation_details:
                component_score = validation_details[component].get('score', 0.0)
                total_score += component_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def validate_multiple_sources(self, sources: List[Source]) -> Dict[str, Any]:
        """Validate multiple sources and provide aggregate assessment"""
        if not sources:
            return {
                'is_valid': False,
                'score': 0.0,
                'errors': ['No sources provided'],
                'warnings': [],
                'source_validations': []
            }
        
        source_validations = []
        all_errors = []
        all_warnings = []
        scores = []
        
        for source in sources:
            validation = self.validate_source(source)
            source_validations.append(validation)
            
            if not validation['is_valid']:
                all_errors.extend(validation['errors'])
            
            all_warnings.extend(validation['warnings'])
            scores.append(validation['score'])
        
        # Calculate aggregate metrics
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        # Determine overall validity
        is_valid = len(all_errors) == 0 and avg_score >= 0.5
        
        return {
            'is_valid': is_valid,
            'score': avg_score,
            'min_score': min_score,
            'max_score': max_score,
            'errors': all_errors,
            'warnings': all_warnings,
            'source_count': len(sources),
            'source_validations': source_validations
        }
