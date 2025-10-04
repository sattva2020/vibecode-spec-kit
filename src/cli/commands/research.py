"""
Research commands for Memory Bank CLI
"""

import argparse
import json
from typing import Dict, List, Any, Optional

from ..core.research import ResearchEngine, ResearchValidator, ResearchCache, SpecConverter
from ..core.research.templates.research_template import ResearchType
from ..utils.output import OutputFormatter
from ..core.config import CLIConfig


class ResearchCommand:
    """Commands for research operations"""
    
    def __init__(self):
        self.research_engine = ResearchEngine()
        self.validator = ResearchValidator()
        self.cache = ResearchCache()
        self.spec_converter = SpecConverter()
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add research command arguments"""
        subparsers = parser.add_subparsers(dest='research_action', help='Research actions')
        
        # Conduct research command
        conduct_parser = subparsers.add_parser('conduct', help='Conduct research')
        conduct_parser.add_argument('query', help='Research query')
        conduct_parser.add_argument('--type', choices=['technical', 'methodology', 'competitive'], 
                                  default='technical', help='Research type')
        conduct_parser.add_argument('--max-sources', type=int, default=10, 
                                  help='Maximum number of sources to collect')
        conduct_parser.add_argument('--force-refresh', action='store_true',
                                  help='Force refresh even if cached results exist')
        conduct_parser.add_argument('--output-file', help='Output file for research results')
        
        # Validate research command
        validate_parser = subparsers.add_parser('validate', help='Validate research results')
        validate_parser.add_argument('--file', required=True, help='Research results file to validate')
        validate_parser.add_argument('--detailed', action='store_true',
                                   help='Show detailed validation results')
        
        # Convert to spec command
        convert_parser = subparsers.add_parser('convert', help='Convert research to specification')
        convert_parser.add_argument('--file', required=True, help='Research results file to convert')
        convert_parser.add_argument('--type', choices=['technical', 'methodology', 'competitive'],
                                  default='technical', help='Conversion type')
        convert_parser.add_argument('--complexity', type=int, choices=[1, 2, 3, 4],
                                  help='Complexity level (auto-detected if not specified)')
        convert_parser.add_argument('--output-file', help='Output file for specification')
        
        # Cache management commands
        cache_parser = subparsers.add_parser('cache', help='Manage research cache')
        cache_subparsers = cache_parser.add_subparsers(dest='cache_action', help='Cache actions')
        
        # Cache stats
        cache_subparsers.add_parser('stats', help='Show cache statistics')
        
        # Cache clear
        cache_subparsers.add_parser('clear', help='Clear research cache')
        
        # Cache search
        cache_search_parser = cache_subparsers.add_parser('search', help='Search cached research')
        cache_search_parser.add_argument('query', help='Search query')
        
        # Cache cleanup
        cache_subparsers.add_parser('cleanup', help='Clean up expired cache entries')
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute research command"""
        try:
            if args.research_action == 'generate':
                return self._generate_template(args, config, formatter)
            elif args.research_action == 'execute':
                return self._execute_research(args, config, formatter)
            elif args.research_action == 'validate':
                return self._validate_research(args, config, formatter)
            elif args.research_action == 'cache':
                return self._manage_cache(args, config, formatter)
            else:
                formatter.error("Unknown research action")
                return 1
        except Exception as e:
            formatter.error(f"Research command failed: {e}")
            return 1
    
    def _generate_template(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Conduct research"""
        formatter.info(f"🔍 Generating {args.type} research template: {args.topic}")
        
        # Map research type
        from ..core.research.validation.research_validator import ResearchType
        research_type_map = {
            'tech': ResearchType.TECHNICAL,
            'methodology': ResearchType.METHODOLOGY,
            'competitive': ResearchType.COMPETITIVE
        }
        
        research_type = research_type_map.get(args.type, ResearchType.TECHNICAL)
        
        # Map depth
        from ..core.research.validation.research_validator import ResearchDepth
        depth_map = {
            'shallow': ResearchDepth.SHALLOW,
            'medium': ResearchDepth.MEDIUM,
            'deep': ResearchDepth.DEEP
        }
        research_depth = depth_map.get(args.depth, ResearchDepth.MEDIUM)
        
        # Conduct research
        formatter.info("📊 Collecting sources and analyzing...")
        # Generate research template
        formatter.info("📊 Generating research template...")
        template = self.research_engine.generate_template(
            topic=args.topic,
            research_type=research_type,
            depth=research_depth
        )
        
        # Display template
        formatter.info("📋 Generated Research Template:")
        formatter.code_block(json.dumps(template, indent=2), "json")
        
        # Save to file
        filename = f"research-{args.topic.lower().replace(' ', '-')}-{args.type}.json"
        self._save_template(template, filename, formatter)
        
        return 0
    
    def _validate_research(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Validate research results"""
        formatter.info(f"✅ Validating research results from: {args.file}")
        
        # Load research results
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                research_data = json.load(f)
        except FileNotFoundError:
            formatter.error(f"File not found: {args.file}")
            return 1
        except json.JSONDecodeError as e:
            formatter.error(f"Invalid JSON file: {e}")
            return 1
        
        # Validate research
        validation_result = self.validator.validate_research(research_data)
        
        # Display validation results
        self._display_validation_results(validation_result, args.detailed, formatter)
        
        return 0 if validation_result['is_valid'] else 1
    
    def _execute_research(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Convert research to specification"""
        formatter.info(f"🔄 Converting research to {args.type} specification")
        
        # Load research results
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                research_data = json.load(f)
        except FileNotFoundError:
            formatter.error(f"File not found: {args.file}")
            return 1
        except json.JSONDecodeError as e:
            formatter.error(f"Invalid JSON file: {e}")
            return 1
        
        # Convert to specification
        spec_data = self.spec_converter.convert_to_spec(
            research_data=research_data,
            research_type=args.type,
            complexity_level=args.complexity
        )
        
        # Display specification
        self._display_specification(spec_data, formatter)
        
        # Save to file if specified
        if args.output_file:
            self._save_specification(spec_data, args.output_file, formatter)
        
        return 0
    
    def _manage_cache(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Manage research cache"""
        if args.cache_action == 'stats':
            return self._show_cache_stats(formatter)
        elif args.cache_action == 'clear':
            return self._clear_cache(formatter)
        elif args.cache_action == 'search':
            return self._search_cache(args, formatter)
        elif args.cache_action == 'cleanup':
            return self._cleanup_cache(formatter)
        else:
            formatter.error("Unknown cache action")
            return 1
    
    def _display_research_results(self, research_result: Any, formatter: OutputFormatter):
        """Display research results"""
        formatter.success("✅ Research completed successfully")
        formatter.info(f"📝 Query: {research_result.query}")
        formatter.info(f"🔬 Type: {research_result.research_type.value}")
        formatter.info(f"📊 Status: {research_result.status.value}")
        
        # Source statistics
        formatter.info(f"📚 Sources: {len(research_result.sources)}")
        if research_result.sources:
            avg_credibility = sum(s.credibility_score for s in research_result.sources) / len(research_result.sources)
            formatter.info(f"🎯 Average credibility: {avg_credibility:.2f}")
        
        # AI analyses
        formatter.info(f"🤖 AI analyses: {len(research_result.ai_analyses)}")
        if research_result.ai_analyses:
            for analysis in research_result.ai_analyses:
                formatter.info(f"   • {analysis.agent_name}: {analysis.confidence_score:.2f} confidence")
        
        # Quality scores
        formatter.info(f"⭐ Confidence score: {research_result.confidence_score:.2f}")
        formatter.info(f"📈 Completeness score: {research_result.completeness_score:.2f}")
        formatter.info(f"🏆 Quality score: {research_result.quality_score:.2f}")
        
        # Key insights
        if research_result.key_insights:
            formatter.info("💡 Key insights:")
            for insight in research_result.key_insights[:3]:  # Show top 3
                formatter.info(f"   • {insight}")
        
        # Recommendations
        if research_result.recommendations:
            formatter.info("🎯 Top recommendations:")
            for rec in research_result.recommendations[:3]:  # Show top 3
                formatter.info(f"   • {rec}")
    
    def _display_validation_results(self, validation_result: Dict[str, Any], detailed: bool, formatter: OutputFormatter):
        """Display validation results"""
        overall_score = validation_result['overall_score']
        is_valid = validation_result['is_valid']
        
        # Overall status
        if is_valid:
            formatter.success(f"✅ Research validation passed (score: {overall_score:.2f})")
        else:
            formatter.error(f"❌ Research validation failed (score: {overall_score:.2f})")
        
        # Dimension scores
        dimension_scores = validation_result.get('dimension_scores', {})
        formatter.info("📊 Validation scores:")
        for dimension, score in dimension_scores.items():
            status_icon = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
            formatter.info(f"   {status_icon} {dimension.title()}: {score:.2f}")
        
        # Errors and warnings
        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])
        
        if errors:
            formatter.error("❌ Errors:")
            for error in errors:
                formatter.error(f"   • {error}")
        
        if warnings:
            formatter.warning("⚠️ Warnings:")
            for warning in warnings:
                formatter.warning(f"   • {warning}")
        
        # Recommendations
        recommendations = validation_result.get('recommendations', [])
        if recommendations:
            formatter.info("💡 Recommendations:")
            for rec in recommendations:
                formatter.info(f"   • {rec}")
        
        # Detailed results
        if detailed:
            formatter.info("🔍 Detailed validation results:")
            formatter.code_block(json.dumps(validation_result, indent=2), "json")
    
    def _display_specification(self, spec_data: Dict[str, Any], formatter: OutputFormatter):
        """Display specification"""
        formatter.success("✅ Specification generated successfully")
        
        # Basic info
        formatter.info(f"📝 Title: {spec_data.get('title', 'Generated Specification')}")
        formatter.info(f"🔬 Type: {spec_data.get('research_type', 'unknown')}")
        formatter.info(f"📊 Complexity: Level {spec_data.get('complexity_level', 'unknown')}")
        
        # Description
        description = spec_data.get('description', '')
        if description:
            formatter.info(f"📄 Description: {description[:200]}{'...' if len(description) > 200 else ''}")
        
        # Implementation guidance
        guidance = spec_data.get('implementation_guidance', {})
        if guidance:
            formatter.info("🎯 Implementation guidance:")
            formatter.info(f"   • Priority: {guidance.get('priority', 'unknown')}")
            formatter.info(f"   • Effort: {guidance.get('estimated_effort', 'unknown')}")
            
            success_factors = guidance.get('success_factors', [])
            if success_factors:
                formatter.info("   • Success factors:")
                for factor in success_factors[:2]:
                    formatter.info(f"     - {factor}")
        
        # Research metadata
        metadata = spec_data.get('research_metadata', {})
        if metadata:
            formatter.info("📊 Research metadata:")
            formatter.info(f"   • Sources: {metadata.get('source_count', 0)}")
            formatter.info(f"   • AI analyses: {metadata.get('ai_analyses_count', 0)}")
            formatter.info(f"   • Confidence: {metadata.get('confidence_score', 0):.2f}")
            formatter.info(f"   • Quality: {metadata.get('quality_score', 0):.2f}")
    
    def _show_cache_stats(self, formatter: OutputFormatter) -> int:
        """Show cache statistics"""
        stats = self.cache.get_cache_stats()
        
        formatter.info("📊 Research Cache Statistics:")
        formatter.info(f"   • Total entries: {stats['total_entries']}")
        formatter.info(f"   • Total size: {stats['total_size_mb']} MB")
        formatter.info(f"   • Cache hits: {stats['cache_hits']}")
        formatter.info(f"   • Cache misses: {stats['cache_misses']}")
        formatter.info(f"   • Hit rate: {stats['hit_rate_percent']}%")
        formatter.info(f"   • TTL: {stats['cache_ttl_hours']} hours")
        formatter.info(f"   • Created: {stats['created_at']}")
        formatter.info(f"   • Last cleanup: {stats['last_cleanup']}")
        
        return 0
    
    def _clear_cache(self, formatter: OutputFormatter) -> int:
        """Clear research cache"""
        if self.cache.clear_cache():
            formatter.success("✅ Research cache cleared successfully")
            return 0
        else:
            formatter.error("❌ Failed to clear research cache")
            return 1
    
    def _search_cache(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Search cached research"""
        formatter.info(f"🔍 Searching cached research: {args.query}")
        
        results = self.cache.search_research(args.query)
        
        if not results:
            formatter.info("No cached research found matching query")
            return 0
        
        formatter.info(f"Found {len(results)} cached research entries:")
        for i, result in enumerate(results, 1):
            research_data = result['research_data']
            formatter.info(f"{i}. {research_data.get('query', 'Unknown query')}")
            formatter.info(f"   Type: {research_data.get('research_type', 'unknown')}")
            formatter.info(f"   Created: {result['created_at']}")
            formatter.info(f"   Match score: {result['match_score']:.2f}")
        
        return 0
    
    def _cleanup_cache(self, formatter: OutputFormatter) -> int:
        """Clean up expired cache entries"""
        cleanup_stats = self.cache.cleanup_cache()
        
        formatter.info("🧹 Cache cleanup completed:")
        formatter.info(f"   • Expired entries removed: {cleanup_stats['expired_removed']}")
        formatter.info(f"   • Old entries removed: {cleanup_stats['old_removed']}")
        formatter.info(f"   • Total removed: {cleanup_stats['total_removed']}")
        formatter.info(f"   • Remaining entries: {cleanup_stats['remaining_entries']}")
        
        return 0
    
    def _save_research_results(self, research_result: Any, filename: str, formatter: OutputFormatter):
        """Save research results to file"""
        try:
            # Convert research result to dictionary
            result_data = {
                'query': research_result.query,
                'research_type': research_result.research_type.value,
                'status': research_result.status.value,
                'sources': [
                    {
                        'url': source.url,
                        'title': source.title,
                        'domain': source.domain,
                        'credibility_score': source.credibility_score,
                        'freshness_score': source.freshness_score,
                        'relevance_score': source.relevance_score
                    }
                    for source in research_result.sources
                ],
                'ai_analyses': [
                    {
                        'agent_name': analysis.agent_name,
                        'analysis_type': analysis.analysis_type,
                        'summary': analysis.summary,
                        'key_findings': analysis.key_findings,
                        'confidence_score': analysis.confidence_score,
                        'recommendations': analysis.recommendations
                    }
                    for analysis in research_result.ai_analyses
                ],
                'synthesized_summary': research_result.synthesized_summary,
                'key_insights': research_result.key_insights,
                'recommendations': research_result.recommendations,
                'confidence_score': research_result.confidence_score,
                'completeness_score': research_result.completeness_score,
                'quality_score': research_result.quality_score,
                'created_at': research_result.created_at.isoformat(),
                'updated_at': research_result.updated_at.isoformat(),
                'metadata': research_result.metadata
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2)
            
            formatter.success(f"✅ Research results saved to: {filename}")
            
        except Exception as e:
            formatter.error(f"❌ Failed to save research results: {e}")
    
    def _save_specification(self, spec_data: Dict[str, Any], filename: str, formatter: OutputFormatter):
        """Save specification to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(spec_data, f, indent=2)
            
            formatter.success(f"✅ Specification saved to: {filename}")
            
        except Exception as e:
            formatter.error(f"❌ Failed to save specification: {e}")
    
    def _save_template(self, template_data: Dict[str, Any], filename: str, formatter: OutputFormatter):
        """Save research template to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            
            formatter.success(f"✅ Research template saved to: {filename}")
            
        except Exception as e:
            formatter.error(f"❌ Failed to save research template: {e}")


# Export command instance
research_command = ResearchCommand()

__all__ = ['research_command']
