"""
Web search engine for collecting research sources
"""

import re
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass

from ..templates.research_template import ResearchType


@dataclass
class WebSearchResult:
    """Represents a web search result"""
    url: str
    title: str
    domain: str
    content: str
    relevance_score: float
    credibility_score: float
    freshness_score: float
    metadata: Dict[str, Any]


class WebSearchEngine:
    """Web search engine for collecting research sources"""
    
    def __init__(self):
        self.search_engines = self._initialize_search_engines()
        self.domain_credibility = self._initialize_domain_credibility()
        self.content_filters = self._initialize_content_filters()
        self.rate_limits = self._initialize_rate_limits()
    
    def _initialize_search_engines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available search engines"""
        return {
            'google': {
                'name': 'Google Search',
                'api_available': False,  # Would need API key in real implementation
                'web_scraping': True,
                'rate_limit': 10,  # requests per minute
                'priority': 1
            },
            'bing': {
                'name': 'Bing Search',
                'api_available': False,  # Would need API key in real implementation
                'web_scraping': True,
                'rate_limit': 15,
                'priority': 2
            },
            'duckduckgo': {
                'name': 'DuckDuckGo',
                'api_available': True,  # Has public API
                'web_scraping': True,
                'rate_limit': 20,
                'priority': 3
            },
            'github': {
                'name': 'GitHub',
                'api_available': True,  # Has public API
                'web_scraping': False,
                'rate_limit': 5000,  # per hour
                'priority': 4
            },
            'stackoverflow': {
                'name': 'Stack Overflow',
                'api_available': True,  # Has public API
                'web_scraping': True,
                'rate_limit': 10000,  # per day
                'priority': 5
            }
        }
    
    def _initialize_domain_credibility(self) -> Dict[str, float]:
        """Initialize domain credibility scores"""
        return {
            # High credibility domains
            'github.com': 0.95,
            'stackoverflow.com': 0.90,
            'docs.python.org': 0.95,
            'developer.mozilla.org': 0.95,
            'nodejs.org': 0.95,
            'reactjs.org': 0.95,
            'vuejs.org': 0.95,
            'angular.io': 0.95,
            'aws.amazon.com': 0.90,
            'cloud.google.com': 0.90,
            'azure.microsoft.com': 0.90,
            'kubernetes.io': 0.95,
            'docker.com': 0.90,
            'redis.io': 0.90,
            'mongodb.com': 0.90,
            'postgresql.org': 0.95,
            'mysql.com': 0.90,
            'apache.org': 0.95,
            'nginx.org': 0.95,
            'elastic.co': 0.90,
            'kibana.org': 0.90,
            'grafana.com': 0.90,
            'prometheus.io': 0.90,
            'jenkins.io': 0.90,
            'gitlab.com': 0.90,
            'bitbucket.org': 0.85,
            'atlassian.com': 0.85,
            'slack.com': 0.85,
            'discord.com': 0.80,
            'telegram.org': 0.80,
            
            # Medium credibility domains
            'medium.com': 0.70,
            'dev.to': 0.75,
            'hashnode.com': 0.70,
            'freecodecamp.org': 0.80,
            'codecademy.com': 0.75,
            'w3schools.com': 0.70,
            'tutorialspoint.com': 0.65,
            'geeksforgeeks.org': 0.75,
            'programiz.com': 0.70,
            'realpython.com': 0.80,
            'python.org': 0.95,
            'npmjs.com': 0.85,
            'pypi.org': 0.90,
            'crates.io': 0.85,
            'rubygems.org': 0.85,
            'packagist.org': 0.85,
            'mvnrepository.com': 0.85,
            'nuget.org': 0.85,
            
            # Lower credibility domains
            'blogspot.com': 0.50,
            'wordpress.com': 0.55,
            'tumblr.com': 0.40,
            'reddit.com': 0.60,
            'quora.com': 0.65,
            'youtube.com': 0.70,
            'vimeo.com': 0.75,
            'slideshare.net': 0.60,
            'scribd.com': 0.55,
            'issuu.com': 0.50
        }
    
    def _initialize_content_filters(self) -> Dict[str, List[str]]:
        """Initialize content filters for different research types"""
        return {
            ResearchType.TECHNICAL.value: {
                'positive_keywords': [
                    'documentation', 'api', 'tutorial', 'guide', 'reference',
                    'implementation', 'example', 'code', 'syntax', 'library',
                    'framework', 'tool', 'utility', 'package', 'module'
                ],
                'negative_keywords': [
                    'job', 'career', 'salary', 'interview', 'resume',
                    'course', 'training', 'certification', 'degree',
                    'news', 'announcement', 'release', 'update'
                ]
            },
            ResearchType.METHODOLOGY.value: {
                'positive_keywords': [
                    'methodology', 'process', 'framework', 'approach', 'practice',
                    'best practice', 'pattern', 'principle', 'guideline', 'standard',
                    'workflow', 'pipeline', 'strategy', 'technique', 'method'
                ],
                'negative_keywords': [
                    'implementation', 'code', 'tutorial', 'example', 'specific',
                    'technical', 'programming', 'development', 'coding'
                ]
            },
            ResearchType.COMPETITIVE.value: {
                'positive_keywords': [
                    'comparison', 'vs', 'alternative', 'competitor', 'competition',
                    'market', 'industry', 'analysis', 'review', 'evaluation',
                    'benchmark', 'feature', 'pricing', 'solution', 'platform'
                ],
                'negative_keywords': [
                    'tutorial', 'guide', 'how to', 'implementation', 'setup',
                    'installation', 'configuration', 'getting started'
                ]
            }
        }
    
    def _initialize_rate_limits(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rate limiting configuration"""
        return {
            'requests_per_minute': 10,
            'requests_per_hour': 100,
            'requests_per_day': 1000,
            'backoff_factor': 2,
            'max_retries': 3
        }
    
    def search(self, 
               query: str, 
               research_type: ResearchType,
               max_results: int = 10,
               use_caching: bool = True) -> List[Dict[str, Any]]:
        """
        Search for sources related to the query
        
        Args:
            query: Search query
            research_type: Type of research being conducted
            max_results: Maximum number of results to return
            use_caching: Whether to use cached results
        
        Returns:
            List of search results
        """
        # Generate search variations based on research type
        search_queries = self._generate_search_queries(query, research_type)
        
        all_results = []
        
        # Search using different engines
        for engine_id, engine_config in self.search_engines.items():
            if engine_config['rate_limit'] > 0:  # Check rate limit
                try:
                    engine_results = self._search_with_engine(
                        engine_id=engine_id,
                        engine_config=engine_config,
                        queries=search_queries,
                        research_type=research_type,
                        max_results=max_results // len(self.search_engines)
                    )
                    
                    all_results.extend(engine_results)
                    
                    # Rate limiting
                    time.sleep(1)  # Simple rate limiting
                    
                except Exception as e:
                    print(f"Error searching with {engine_id}: {e}")
                    continue
        
        # Filter and rank results
        filtered_results = self._filter_results(all_results, research_type)
        ranked_results = self._rank_results(filtered_results, research_type)
        
        # Remove duplicates
        unique_results = self._remove_duplicates(ranked_results)
        
        return unique_results[:max_results]
    
    def _generate_search_queries(self, query: str, research_type: ResearchType) -> List[str]:
        """Generate search query variations based on research type"""
        base_query = query.lower()
        
        # Base queries
        queries = [query, base_query]
        
        # Add type-specific modifiers
        if research_type == ResearchType.TECHNICAL:
            queries.extend([
                f"{query} documentation",
                f"{query} tutorial",
                f"{query} implementation",
                f"{query} examples",
                f"{query} API reference"
            ])
        elif research_type == ResearchType.METHODOLOGY:
            queries.extend([
                f"{query} methodology",
                f"{query} best practices",
                f"{query} framework",
                f"{query} approach",
                f"{query} process"
            ])
        elif research_type == ResearchType.COMPETITIVE:
            queries.extend([
                f"{query} vs alternatives",
                f"{query} comparison",
                f"{query} competitors",
                f"{query} market analysis",
                f"{query} review"
            ])
        
        return list(set(queries))  # Remove duplicates
    
    def _search_with_engine(self, 
                           engine_id: str,
                           engine_config: Dict[str, Any],
                           queries: List[str],
                           research_type: ResearchType,
                           max_results: int) -> List[Dict[str, Any]]:
        """Search using a specific engine"""
        
        # Simulate search results (in real implementation, this would call actual APIs)
        results = []
        
        for query in queries[:3]:  # Limit queries per engine
            engine_results = self._simulate_search_results(
                engine_id=engine_id,
                query=query,
                research_type=research_type,
                max_results=max_results // len(queries)
            )
            results.extend(engine_results)
        
        return results
    
    def _simulate_search_results(self, 
                                engine_id: str,
                                query: str,
                                research_type: ResearchType,
                                max_results: int) -> List[Dict[str, Any]]:
        """Simulate search results (placeholder for actual API calls)"""
        
        # Generate mock results based on query and research type
        results = []
        
        # Common domains for different research types
        domain_templates = {
            ResearchType.TECHNICAL: [
                'github.com', 'stackoverflow.com', 'docs.python.org', 
                'developer.mozilla.org', 'nodejs.org', 'reactjs.org'
            ],
            ResearchType.METHODOLOGY: [
                'medium.com', 'dev.to', 'freecodecamp.org', 
                'atlassian.com', 'slack.com', 'hashnode.com'
            ],
            ResearchType.COMPETITIVE: [
                'crunchbase.com', 'techcrunch.com', 'venturebeat.com',
                'forbes.com', 'wired.com', 'arstechnica.com'
            ]
        }
        
        domains = domain_templates.get(research_type, domain_templates[ResearchType.TECHNICAL])
        
        for i in range(max_results):
            domain = domains[i % len(domains)]
            
            result = {
                'url': f"https://{domain}/article/{hashlib.md5(f'{query}_{i}'.encode()).hexdigest()[:8]}",
                'title': f"{query.title()} - {research_type.value} Analysis and Guide",
                'domain': domain,
                'content': self._generate_mock_content(query, research_type),
                'relevance_score': self._calculate_relevance_score(query, research_type),
                'credibility_score': self.domain_credibility.get(domain, 0.5),
                'freshness_score': 0.8 + (i * 0.02),  # Simulate freshness variation
                'metadata': {
                    'engine': engine_id,
                    'search_query': query,
                    'result_index': i,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            results.append(result)
        
        return results
    
    def _generate_mock_content(self, query: str, research_type: ResearchType) -> str:
        """Generate mock content based on query and research type"""
        
        if research_type == ResearchType.TECHNICAL:
            return f"""
            Technical analysis of {query} including implementation details, 
            performance characteristics, security considerations, and best practices. 
            This comprehensive guide covers API usage, code examples, and integration patterns.
            """
        elif research_type == ResearchType.METHODOLOGY:
            return f"""
            Methodology overview for {query} covering process steps, best practices, 
            team requirements, and success factors. This guide provides practical 
            implementation advice and common pitfalls to avoid.
            """
        elif research_type == ResearchType.COMPETITIVE:
            return f"""
            Competitive analysis of {query} market landscape, key players, 
            positioning strategies, and market trends. This analysis provides 
            insights into competitive advantages and market opportunities.
            """
        else:
            return f"Comprehensive analysis and insights about {query}."
    
    def _calculate_relevance_score(self, query: str, research_type: ResearchType) -> float:
        """Calculate relevance score for a result"""
        # Simple relevance calculation based on keyword matching
        query_words = set(query.lower().split())
        
        # Get positive keywords for research type
        filters = self.content_filters.get(research_type.value, {})
        positive_keywords = set(filters.get('positive_keywords', []))
        
        # Calculate overlap
        overlap = len(query_words.intersection(positive_keywords))
        max_possible = len(positive_keywords)
        
        base_score = overlap / max_possible if max_possible > 0 else 0.5
        
        # Add some randomness to simulate real search results
        import random
        variation = random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, base_score + variation))
    
    def _filter_results(self, results: List[Dict[str, Any]], research_type: ResearchType) -> List[Dict[str, Any]]:
        """Filter results based on research type and quality"""
        
        filters = self.content_filters.get(research_type.value, {})
        positive_keywords = set(filters.get('positive_keywords', []))
        negative_keywords = set(filters.get('negative_keywords', []))
        
        filtered_results = []
        
        for result in results:
            # Check content for positive keywords
            content_lower = result['content'].lower()
            title_lower = result['title'].lower()
            combined_text = f"{content_lower} {title_lower}"
            
            # Skip if contains negative keywords
            if any(neg_word in combined_text for neg_word in negative_keywords):
                continue
            
            # Boost score if contains positive keywords
            positive_matches = sum(1 for pos_word in positive_keywords if pos_word in combined_text)
            if positive_matches > 0:
                result['relevance_score'] = min(1.0, result['relevance_score'] + 0.1 * positive_matches)
            
            # Filter by minimum quality thresholds
            if (result['relevance_score'] >= 0.3 and 
                result['credibility_score'] >= 0.4 and 
                result['freshness_score'] >= 0.5):
                filtered_results.append(result)
        
        return filtered_results
    
    def _rank_results(self, results: List[Dict[str, Any]], research_type: ResearchType) -> List[Dict[str, Any]]:
        """Rank results based on multiple factors"""
        
        def calculate_rank_score(result):
            # Weighted scoring
            relevance_weight = 0.4
            credibility_weight = 0.3
            freshness_weight = 0.2
            domain_bonus = 0.1
            
            # Domain bonus for high-credibility domains
            domain_score = 0.0
            if result['domain'] in self.domain_credibility:
                if self.domain_credibility[result['domain']] >= 0.8:
                    domain_score = 0.1
                elif self.domain_credibility[result['domain']] >= 0.6:
                    domain_score = 0.05
            
            rank_score = (
                result['relevance_score'] * relevance_weight +
                result['credibility_score'] * credibility_weight +
                result['freshness_score'] * freshness_weight +
                domain_score
            )
            
            return rank_score
        
        # Sort by rank score
        ranked_results = sorted(results, key=calculate_rank_score, reverse=True)
        
        # Add rank score to metadata
        for i, result in enumerate(ranked_results):
            result['metadata']['rank_score'] = calculate_rank_score(result)
            result['metadata']['rank_position'] = i + 1
        
        return ranked_results
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL and title similarity"""
        
        seen_urls = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            url = result['url']
            title = result['title'].lower()
            
            # Check for exact URL match
            if url in seen_urls:
                continue
            
            # Check for similar title (simple similarity check)
            title_words = set(title.split())
            is_duplicate = False
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                similarity = len(title_words.intersection(seen_words)) / len(title_words.union(seen_words))
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_results.append(result)
        
        return unique_results
