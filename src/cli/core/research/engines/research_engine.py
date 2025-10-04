"""
Main research engine for conducting comprehensive research
"""

import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from ..templates.research_template import ResearchTemplate, ResearchType, ResearchStatus, ResearchResult
from ..validation.research_validator import ResearchValidator
from ..cache.research_cache import ResearchCache
from .ai_research_engine import AIResearchEngine
from .web_search_engine import WebSearchEngine


class ResearchEngine:
    """Main research engine coordinating all research activities"""
    
    def __init__(self, cache_directory: str = "memory-bank/.research_cache"):
        self.validator = ResearchValidator()
        self.cache = ResearchCache(cache_directory)
        self.ai_engine = AIResearchEngine()
        self.web_engine = WebSearchEngine()
        self.active_research: Dict[str, ResearchResult] = {}
    
    def generate_template(self, topic: str, research_type: ResearchType, 
                         depth = None) -> Dict[str, Any]:
        """Generate research template"""
        from ..templates.research_template import ResearchTemplate
        from ..templates.tech_research_template import TechResearchTemplate
        from ..templates.methodology_template import MethodologyTemplate
        from ..templates.competitive_template import CompetitiveTemplate
        
        # Select appropriate template
        if research_type.value == 'technical':
            template = TechResearchTemplate()
        elif research_type.value == 'methodology':
            template = MethodologyTemplate()
        elif research_type.value == 'competitive':
            template = CompetitiveTemplate()
        else:
            template = ResearchTemplate()
        
        # Generate template data
        from ..validation.research_validator import ResearchDepth
        template_data = template.generate_template(
            topic=topic,
            depth=depth or ResearchDepth.MEDIUM
        )
        
        return template_data
    
    def conduct_research(self, 
                        query: str, 
                        research_type: ResearchType,
                        force_refresh: bool = False,
                        max_sources: int = 10) -> ResearchResult:
        """
        Conduct comprehensive research on a given query
        
        Args:
            query: Research query
            research_type: Type of research to conduct
            force_refresh: Force refresh even if cached results exist
            max_sources: Maximum number of sources to collect
        
        Returns:
            ResearchResult with complete research data
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, research_type)
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = self.cache.get_research(cache_key)
            if cached_result:
                return self._deserialize_research_result(cached_result)
        
        # Create research template
        template = self._get_research_template(research_type)
        
        # Initialize research result
        research_result = ResearchResult(
            query=query,
            research_type=research_type,
            status=ResearchStatus.IN_PROGRESS,
            sources=[],
            ai_analyses=[],
            synthesized_summary="",
            key_insights=[],
            recommendations=[],
            confidence_score=0.0,
            completeness_score=0.0,
            quality_score=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        # Store active research
        self.active_research[cache_key] = research_result
        
        try:
            # Conduct research phases
            self._phase_1_source_collection(research_result, max_sources)
            self._phase_2_ai_analysis(research_result)
            self._phase_3_synthesis(research_result)
            self._phase_4_validation(research_result)
            
            # Update status
            research_result.status = ResearchStatus.COMPLETED
            research_result.updated_at = datetime.now()
            
            # Cache results
            self.cache.store_research(cache_key, self._serialize_research_result(research_result))
            
        except Exception as e:
            research_result.status = ResearchStatus.FAILED
            research_result.metadata['error'] = str(e)
            research_result.updated_at = datetime.now()
        
        finally:
            # Remove from active research
            if cache_key in self.active_research:
                del self.active_research[cache_key]
        
        return research_result
    
    def _phase_1_source_collection(self, research_result: ResearchResult, max_sources: int):
        """Phase 1: Collect sources from web search"""
        # Use web search engine to find sources
        web_results = self.web_engine.search(
            query=research_result.query,
            research_type=research_result.research_type,
            max_results=max_sources
        )
        
        # Convert web results to Source objects
        research_result.sources = [
            self._convert_to_source(web_result) 
            for web_result in web_results[:max_sources]
        ]
        
        # Update completeness score
        research_result.completeness_score = min(len(research_result.sources) / max_sources, 1.0)
    
    def _phase_2_ai_analysis(self, research_result: ResearchResult):
        """Phase 2: AI analysis of collected sources"""
        if not research_result.sources:
            return
        
        # Use AI engine to analyze sources
        ai_analyses = self.ai_engine.analyze_sources(
            sources=research_result.sources,
            research_type=research_result.research_type,
            query=research_result.query
        )
        
        research_result.ai_analyses = ai_analyses
        
        # Calculate confidence score based on AI analyses
        if ai_analyses:
            confidence_scores = [analysis.confidence_score for analysis in ai_analyses]
            research_result.confidence_score = sum(confidence_scores) / len(confidence_scores)
    
    def _phase_3_synthesis(self, research_result: ResearchResult):
        """Phase 3: Synthesize results from AI analyses"""
        if not research_result.ai_analyses:
            return
        
        # Use AI engine to synthesize results
        synthesis = self.ai_engine.synthesize_analyses(
            analyses=research_result.ai_analyses,
            research_type=research_result.research_type
        )
        
        research_result.synthesized_summary = synthesis.get('summary', '')
        research_result.key_insights = synthesis.get('insights', [])
        research_result.recommendations = synthesis.get('recommendations', [])
    
    def _phase_4_validation(self, research_result: ResearchResult):
        """Phase 4: Validate research quality and completeness"""
        validation_result = self.validator.validate_research(research_result)
        
        # Update quality score
        research_result.quality_score = validation_result.get('overall_score', 0.0)
        
        # Add validation metadata
        research_result.metadata['validation'] = validation_result
    
    def _get_research_template(self, research_type: ResearchType) -> ResearchTemplate:
        """Get appropriate research template based on type"""
        from ..templates.tech_research_template import TechResearchTemplate
        from ..templates.methodology_template import MethodologyTemplate
        
        if research_type == ResearchType.TECHNICAL:
            return TechResearchTemplate()
        elif research_type == ResearchType.METHODOLOGY:
            return MethodologyTemplate()
        else:
            return ResearchTemplate(research_type)
    
    def _convert_to_source(self, web_result: Dict[str, Any]) -> 'Source':
        """Convert web search result to Source object"""
        from ..templates.research_template import Source
        
        return Source(
            url=web_result.get('url', ''),
            title=web_result.get('title', ''),
            domain=web_result.get('domain', ''),
            content=web_result.get('content', ''),
            credibility_score=web_result.get('credibility_score', 0.5),
            freshness_score=web_result.get('freshness_score', 0.5),
            relevance_score=web_result.get('relevance_score', 0.5),
            accessed_at=datetime.now(),
            metadata=web_result.get('metadata', {})
        )
    
    def _generate_cache_key(self, query: str, research_type: ResearchType) -> str:
        """Generate cache key for research query"""
        key_string = f"{query}_{research_type.value}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_research_result(self, research_result: ResearchResult) -> Dict[str, Any]:
        """Serialize research result for caching"""
        # Convert datetime objects to strings
        data = asdict(research_result)
        data['created_at'] = research_result.created_at.isoformat()
        data['updated_at'] = research_result.updated_at.isoformat()
        
        for source in data['sources']:
            if 'accessed_at' in source:
                source['accessed_at'] = source['accessed_at'].isoformat()
        
        return data
    
    def _deserialize_research_result(self, data: Dict[str, Any]) -> ResearchResult:
        """Deserialize cached research result"""
        # Convert string dates back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        for source in data['sources']:
            if 'accessed_at' in source and isinstance(source['accessed_at'], str):
                source['accessed_at'] = datetime.fromisoformat(source['accessed_at'])
        
        return ResearchResult(**data)
    
    def get_research_status(self, cache_key: str) -> Optional[ResearchStatus]:
        """Get status of ongoing research"""
        if cache_key in self.active_research:
            return self.active_research[cache_key].status
        return None
    
    def cancel_research(self, cache_key: str) -> bool:
        """Cancel ongoing research"""
        if cache_key in self.active_research:
            research_result = self.active_research[cache_key]
            research_result.status = ResearchStatus.FAILED
            research_result.metadata['cancelled'] = True
            del self.active_research[cache_key]
            return True
        return False
    
    def get_research_history(self, limit: int = 10) -> List[ResearchResult]:
        """Get recent research history"""
        return self.cache.get_recent_research(limit)
    
    def search_research_history(self, query: str) -> List[ResearchResult]:
        """Search through research history"""
        return self.cache.search_research(query)
