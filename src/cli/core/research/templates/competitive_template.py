"""
Competitive analysis research template
"""

from typing import Dict, Any, List
from datetime import datetime
from .research_template import ResearchTemplate


class CompetitiveTemplate(ResearchTemplate):
    """Template for competitive analysis research"""
    
    def __init__(self):
        super().__init__()
        self.template_type = "competitive_analysis"
        self.validation_rules.update({
            'min_competitors': 3,
            'max_competitors': 10,
            'required_analysis_sections': [
                'market_overview',
                'competitor_profiles',
                'feature_comparison',
                'pricing_analysis',
                'strengths_weaknesses',
                'market_positioning',
                'recommendations'
            ]
        })
    
    def get_research_fields(self) -> Dict[str, Any]:
        """Get competitive research fields"""
        base_fields = super().get_research_fields()
        
        competitive_fields = {
            "market_overview": {
                "description": "Market size, trends, and key players",
                "required": True,
                "type": "text"
            },
            "competitor_profiles": {
                "description": "Detailed profiles of main competitors",
                "required": True,
                "type": "list"
            },
            "feature_comparison": {
                "description": "Feature-by-feature comparison matrix",
                "required": True,
                "type": "table"
            },
            "pricing_analysis": {
                "description": "Pricing models and strategies analysis",
                "required": True,
                "type": "text"
            },
            "strengths_weaknesses": {
                "description": "SWOT analysis for each competitor",
                "required": True,
                "type": "text"
            },
            "market_positioning": {
                "description": "Market positioning and differentiation strategies",
                "required": True,
                "type": "text"
            },
            "recommendations": {
                "description": "Strategic recommendations based on analysis",
                "required": True,
                "type": "text"
            }
        }
        
        # Merge with base fields
        base_fields.update(competitive_fields)
        return base_fields
    
    def generate_template(self, topic: str, depth) -> Dict[str, Any]:
        """Generate competitive research template"""
        template_data = super().generate_template(topic, depth)
        
        # Add competitive-specific fields
        template_data.update({
            "competitive_analysis": {
                "target_market": "",
                "competitors": [],
                "analysis_framework": "SWOT + Feature Matrix",
                "research_methodology": "Desktop research + Public data analysis"
            },
            "metadata": {
                **template_data["metadata"],
                "template_type": "competitive_analysis",
                "analysis_depth": depth.value if hasattr(depth, 'value') else str(depth)
            }
        })
        
        return template_data
