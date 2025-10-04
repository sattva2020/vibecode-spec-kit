"""
Credibility scorer for assessing source and content credibility
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class CredibilityScorer:
    """Scorer for assessing credibility of sources and content"""
    
    def __init__(self):
        self.authority_domains = self._initialize_authority_domains()
        self.authority_indicators = self._initialize_authority_indicators()
        self.credibility_factors = self._initialize_credibility_factors()
    
    def _initialize_authority_domains(self) -> Dict[str, Dict[str, Any]]:
        """Initialize authority domain scoring"""
        return {
            # Government and Educational (0.95-1.0)
            'gov': {'score': 0.98, 'type': 'government'},
            'edu': {'score': 0.95, 'type': 'educational'},
            'ac.uk': {'score': 0.95, 'type': 'educational'},
            'edu.au': {'score': 0.95, 'type': 'educational'},
            
            # Major Tech Companies (0.9-0.95)
            'google.com': {'score': 0.95, 'type': 'tech_corporate'},
            'microsoft.com': {'score': 0.93, 'type': 'tech_corporate'},
            'amazon.com': {'score': 0.92, 'type': 'tech_corporate'},
            'apple.com': {'score': 0.92, 'type': 'tech_corporate'},
            'meta.com': {'score': 0.90, 'type': 'tech_corporate'},
            
            # Open Source Projects (0.85-0.95)
            'github.com': {'score': 0.95, 'type': 'open_source'},
            'apache.org': {'score': 0.95, 'type': 'open_source'},
            'python.org': {'score': 0.95, 'type': 'open_source'},
            'nodejs.org': {'score': 0.95, 'type': 'open_source'},
            'kubernetes.io': {'score': 0.95, 'type': 'open_source'},
            
            # Documentation Sites (0.85-0.95)
            'docs.python.org': {'score': 0.95, 'type': 'documentation'},
            'developer.mozilla.org': {'score': 0.95, 'type': 'documentation'},
            'reactjs.org': {'score': 0.95, 'type': 'documentation'},
            'vuejs.org': {'score': 0.95, 'type': 'documentation'},
            'angular.io': {'score': 0.95, 'type': 'documentation'},
            
            # Technical Communities (0.8-0.9)
            'stackoverflow.com': {'score': 0.90, 'type': 'community'},
            'stackexchange.com': {'score': 0.90, 'type': 'community'},
            'reddit.com': {'score': 0.70, 'type': 'community'},
            'hackernews.ycombinator.com': {'score': 0.85, 'type': 'community'},
            
            # Professional Platforms (0.75-0.9)
            'linkedin.com': {'score': 0.80, 'type': 'professional'},
            'medium.com': {'score': 0.70, 'type': 'professional'},
            'dev.to': {'score': 0.75, 'type': 'professional'},
            'hashnode.com': {'score': 0.70, 'type': 'professional'},
            
            # News and Media (0.6-0.8)
            'techcrunch.com': {'score': 0.80, 'type': 'news'},
            'arstechnica.com': {'score': 0.85, 'type': 'news'},
            'wired.com': {'score': 0.80, 'type': 'news'},
            'theverge.com': {'score': 0.75, 'type': 'news'},
            
            # Educational Platforms (0.7-0.85)
            'coursera.org': {'score': 0.85, 'type': 'education'},
            'udacity.com': {'score': 0.80, 'type': 'education'},
            'edx.org': {'score': 0.85, 'type': 'education'},
            'khanacademy.org': {'score': 0.85, 'type': 'education'}
        }
    
    def _initialize_authority_indicators(self) -> Dict[str, List[str]]:
        """Initialize authority indicators in content"""
        return {
            'high_authority': [
                'peer reviewed', 'research study', 'scientific paper',
                'official documentation', 'technical specification',
                'industry standard', 'best practice', 'expert consensus',
                'published by', 'authored by', 'written by expert'
            ],
            'medium_authority': [
                'tutorial', 'guide', 'how to', 'step by step',
                'example', 'demo', 'case study', 'implementation',
                'based on', 'according to', 'referenced'
            ],
            'low_authority': [
                'opinion', 'personal experience', 'my thoughts',
                'i believe', 'in my opinion', 'i think',
                'rumor', 'hearsay', 'unconfirmed'
            ]
        }
    
    def _initialize_credibility_factors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize credibility scoring factors"""
        return {
            'domain_authority': {
                'weight': 0.4,
                'description': 'Authority of the domain hosting the content'
            },
            'content_authority': {
                'weight': 0.25,
                'description': 'Authority indicators in the content itself'
            },
            'source_attribution': {
                'weight': 0.15,
                'description': 'Quality of source attribution and references'
            },
            'content_quality': {
                'weight': 0.10,
                'description': 'Overall quality of content presentation'
            },
            'freshness_factor': {
                'weight': 0.05,
                'description': 'How recent the content is'
            },
            'engagement_quality': {
                'weight': 0.05,
                'description': 'Quality of engagement and discussion'
            }
        }
    
    def score_source(self, url: str, domain: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        Score the credibility of a source
        
        Args:
            url: Source URL
            domain: Source domain
            content: Source content
            title: Source title
        
        Returns:
            Credibility scoring results
        """
        scoring_result = {
            'overall_score': 0.0,
            'factor_scores': {},
            'confidence': 0.0,
            'recommendations': []
        }
        
        # Score domain authority
        domain_score = self._score_domain_authority(domain)
        scoring_result['factor_scores']['domain_authority'] = domain_score
        
        # Score content authority
        content_score = self._score_content_authority(content, title)
        scoring_result['factor_scores']['content_authority'] = content_score
        
        # Score source attribution
        attribution_score = self._score_source_attribution(content)
        scoring_result['factor_scores']['source_attribution'] = attribution_score
        
        # Score content quality
        quality_score = self._score_content_quality(content, title)
        scoring_result['factor_scores']['content_quality'] = quality_score
        
        # Score freshness factor
        freshness_score = self._score_freshness_factor(url, content)
        scoring_result['factor_scores']['freshness_factor'] = freshness_score
        
        # Score engagement quality
        engagement_score = self._score_engagement_quality(content)
        scoring_result['factor_scores']['engagement_quality'] = engagement_score
        
        # Calculate weighted overall score
        scoring_result['overall_score'] = self._calculate_weighted_score(scoring_result['factor_scores'])
        
        # Calculate confidence
        scoring_result['confidence'] = self._calculate_confidence(scoring_result['factor_scores'])
        
        # Generate recommendations
        scoring_result['recommendations'] = self._generate_credibility_recommendations(scoring_result)
        
        return scoring_result
    
    def _score_domain_authority(self, domain: str) -> float:
        """Score domain authority"""
        if not domain:
            return 0.0
        
        # Check exact domain match
        if domain in self.authority_domains:
            return self.authority_domains[domain]['score']
        
        # Check subdomain matches
        domain_parts = domain.split('.')
        for i in range(len(domain_parts)):
            subdomain = '.'.join(domain_parts[i:])
            if subdomain in self.authority_domains:
                # Slight penalty for subdomains
                return self.authority_domains[subdomain]['score'] * 0.9
        
        # Check TLD-based scoring
        tld = domain_parts[-1] if domain_parts else ''
        if tld in ['gov', 'edu', 'org']:
            return 0.8
        elif tld in ['com', 'net']:
            return 0.6
        else:
            return 0.5
    
    def _score_content_authority(self, content: str, title: str = "") -> float:
        """Score content authority indicators"""
        combined_text = f"{title} {content}".lower()
        score = 0.5  # Base score
        
        # Check for high authority indicators
        high_authority_matches = sum(1 for indicator in self.authority_indicators['high_authority']
                                   if indicator in combined_text)
        score += high_authority_matches * 0.1
        
        # Check for medium authority indicators
        medium_authority_matches = sum(1 for indicator in self.authority_indicators['medium_authority']
                                     if indicator in combined_text)
        score += medium_authority_matches * 0.05
        
        # Check for low authority indicators
        low_authority_matches = sum(1 for indicator in self.authority_indicators['low_authority']
                                  if indicator in combined_text)
        score -= low_authority_matches * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _score_source_attribution(self, content: str) -> float:
        """Score quality of source attribution"""
        score = 0.5  # Base score
        
        # Check for references and citations
        reference_patterns = [
            r'\[[\d]+\]',  # [1], [2], etc.
            r'\(\d{4}\)',  # (2024), (2023), etc.
            r'ref:\s*\w+',  # ref: something
            r'see\s+also',  # see also
            r'according\s+to',  # according to
            r'source:',  # source:
            r'reference:',  # reference:
            r'cite:',  # cite:
            r'link:',  # link:
            r'url:',  # url:
        ]
        
        attribution_count = 0
        for pattern in reference_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            attribution_count += len(matches)
        
        # Bonus for multiple attributions
        if attribution_count >= 3:
            score += 0.3
        elif attribution_count >= 2:
            score += 0.2
        elif attribution_count >= 1:
            score += 0.1
        
        return min(1.0, score)
    
    def _score_content_quality(self, content: str, title: str = "") -> float:
        """Score overall content quality"""
        score = 0.5  # Base score
        
        # Length bonus
        content_length = len(content)
        if content_length >= 1000:
            score += 0.2
        elif content_length >= 500:
            score += 0.1
        elif content_length < 100:
            score -= 0.2
        
        # Structure indicators
        structure_indicators = [
            r'#+\s+',  # Headers
            r'\*\*.*?\*\*',  # Bold text
            r'```.*?```',  # Code blocks
            r'^\d+\.\s+',  # Numbered lists
            r'^[-*]\s+',  # Bullet points
        ]
        
        structure_count = 0
        for pattern in structure_indicators:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            structure_count += len(matches)
        
        if structure_count >= 5:
            score += 0.2
        elif structure_count >= 3:
            score += 0.1
        
        # Technical content indicators
        technical_indicators = [
            'function', 'class', 'method', 'algorithm', 'data structure',
            'implementation', 'configuration', 'installation', 'deployment',
            'api', 'endpoint', 'database', 'server', 'client'
        ]
        
        technical_count = sum(1 for indicator in technical_indicators
                            if indicator in content.lower())
        
        if technical_count >= 5:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _score_freshness_factor(self, url: str, content: str) -> float:
        """Score freshness factor"""
        score = 0.5  # Base score
        
        # Check for date indicators in URL
        date_patterns = [
            r'/(\d{4})/',  # /2024/
            r'/(\d{4}-\d{2})/',  # /2024-01/
            r'/(\d{4}-\d{2}-\d{2})/',  # /2024-01-15/
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, url)
            if matches:
                try:
                    year = int(matches[0][:4])
                    current_year = datetime.now().year
                    if year >= current_year - 1:
                        score += 0.3
                    elif year >= current_year - 3:
                        score += 0.1
                    else:
                        score -= 0.1
                except ValueError:
                    pass
        
        # Check for date indicators in content
        content_date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # 2024-01-15
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 1/15/2024
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',  # January 2024
        ]
        
        for pattern in content_date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += 0.1
                break
        
        return max(0.0, min(1.0, score))
    
    def _score_engagement_quality(self, content: str) -> float:
        """Score engagement quality"""
        score = 0.5  # Base score
        
        # Check for interactive elements
        engagement_indicators = [
            'comment', 'discussion', 'feedback', 'review',
            'rating', 'like', 'share', 'subscribe',
            'forum', 'community', 'user', 'participant'
        ]
        
        engagement_count = sum(1 for indicator in engagement_indicators
                             if indicator in content.lower())
        
        if engagement_count >= 3:
            score += 0.2
        elif engagement_count >= 1:
            score += 0.1
        
        # Check for question-answer patterns
        qa_patterns = [
            r'\?.*?answer',
            r'question.*?\?',
            r'faq',
            r'q:\s*.*?\n\s*a:\s*',
        ]
        
        qa_count = 0
        for pattern in qa_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            qa_count += len(matches)
        
        if qa_count >= 2:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_weighted_score(self, factor_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        total_weight = 0.0
        
        for factor, score in factor_scores.items():
            if factor in self.credibility_factors:
                weight = self.credibility_factors[factor]['weight']
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_confidence(self, factor_scores: Dict[str, float]) -> float:
        """Calculate confidence in the credibility score"""
        if not factor_scores:
            return 0.0
        
        # Higher confidence when multiple factors agree
        scores = list(factor_scores.values())
        mean_score = sum(scores) / len(scores)
        
        # Calculate variance (lower variance = higher confidence)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Convert variance to confidence (lower variance = higher confidence)
        confidence = max(0.0, 1.0 - variance)
        
        return confidence
    
    def _generate_credibility_recommendations(self, scoring_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving credibility"""
        recommendations = []
        factor_scores = scoring_result['factor_scores']
        
        # Domain authority recommendations
        if factor_scores.get('domain_authority', 0) < 0.6:
            recommendations.append("Consider using sources from more authoritative domains")
        
        # Content authority recommendations
        if factor_scores.get('content_authority', 0) < 0.6:
            recommendations.append("Look for content with more authority indicators (peer review, official documentation)")
        
        # Source attribution recommendations
        if factor_scores.get('source_attribution', 0) < 0.6:
            recommendations.append("Prefer sources with better attribution and references")
        
        # Content quality recommendations
        if factor_scores.get('content_quality', 0) < 0.6:
            recommendations.append("Look for more comprehensive and well-structured content")
        
        # Freshness recommendations
        if factor_scores.get('freshness_factor', 0) < 0.6:
            recommendations.append("Consider more recent sources when available")
        
        return recommendations
