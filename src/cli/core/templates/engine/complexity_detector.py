# src/cli/core/templates/engine/complexity_detector.py
"""
Complexity Detection Engine for automatically determining task complexity levels.
Analyzes task descriptions and context to suggest appropriate template levels.
"""

from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass


@dataclass
class ComplexityIndicators:
    """Indicators used for complexity detection."""
    keywords: List[str]
    patterns: List[str]
    weight: float


@dataclass
class ComplexityResult:
    """Result of complexity detection analysis."""
    level: int
    confidence: float
    indicators: List[str]
    reasoning: str


class ComplexityDetector:
    """
    Automatic complexity detection based on task descriptions and context.
    Uses keyword analysis, pattern matching, and contextual clues.
    """
    
    def __init__(self):
        self.complexity_indicators = self._initialize_complexity_indicators()
        self.keyword_weights = self._initialize_keyword_weights()
        self.pattern_weights = self._initialize_pattern_weights()
    
    def _initialize_complexity_indicators(self) -> Dict[int, ComplexityIndicators]:
        """Initialize complexity indicators for each level."""
        return {
            1: ComplexityIndicators(
                keywords=[
                    "fix", "bug", "typo", "error", "issue", "problem",
                    "update", "change", "modify", "adjust", "correct",
                    "simple", "quick", "minor", "small", "easy"
                ],
                patterns=[
                    r"fix\s+\w+",
                    r"update\s+\w+",
                    r"change\s+\w+",
                    r"correct\s+\w+",
                    r"typo\s+in",
                    r"small\s+\w+",
                    r"quick\s+\w+"
                ],
                weight=1.0
            ),
            2: ComplexityIndicators(
                keywords=[
                    "enhance", "improve", "optimize", "refactor", "update",
                    "add", "new", "feature", "functionality", "capability",
                    "medium", "moderate", "standard"
                ],
                patterns=[
                    r"add\s+\w+\s+feature",
                    r"enhance\s+\w+",
                    r"improve\s+\w+",
                    r"new\s+\w+",
                    r"implement\s+\w+",
                    r"create\s+\w+"
                ],
                weight=2.0
            ),
            3: ComplexityIndicators(
                keywords=[
                    "implement", "develop", "create", "build", "design",
                    "architecture", "system", "integration", "api", "service",
                    "complex", "advanced", "comprehensive", "detailed"
                ],
                patterns=[
                    r"implement\s+\w+\s+system",
                    r"develop\s+\w+\s+feature",
                    r"create\s+\w+\s+architecture",
                    r"build\s+\w+\s+integration",
                    r"design\s+\w+\s+system",
                    r"complex\s+\w+",
                    r"advanced\s+\w+"
                ],
                weight=3.0
            ),
            4: ComplexityIndicators(
                keywords=[
                    "architecture", "system", "platform", "framework",
                    "infrastructure", "enterprise", "scalable", "distributed",
                    "microservices", "cloud", "database", "security",
                    "performance", "optimization", "enterprise", "critical"
                ],
                patterns=[
                    r"enterprise\s+\w+",
                    r"scalable\s+\w+",
                    r"distributed\s+\w+",
                    r"microservices\s+\w+",
                    r"cloud\s+\w+",
                    r"infrastructure\s+\w+",
                    r"critical\s+\w+",
                    r"platform\s+\w+"
                ],
                weight=4.0
            )
        }
    
    def _initialize_keyword_weights(self) -> Dict[str, float]:
        """Initialize keyword weights for complexity scoring."""
        return {
            # Level 1 keywords
            "fix": 1.0, "bug": 1.0, "typo": 0.5, "error": 1.0,
            "update": 1.0, "change": 1.0, "simple": 0.5, "quick": 0.5,
            
            # Level 2 keywords
            "enhance": 2.0, "improve": 2.0, "add": 2.0, "new": 2.0,
            "feature": 2.0, "refactor": 2.0, "optimize": 2.0,
            
            # Level 3 keywords
            "implement": 3.0, "develop": 3.0, "create": 3.0,
            "build": 3.0, "design": 3.0, "integration": 3.0,
            "api": 3.0, "service": 3.0, "complex": 3.0,
            
            # Level 4 keywords
            "architecture": 4.0, "system": 4.0, "platform": 4.0,
            "enterprise": 4.0, "scalable": 4.0, "distributed": 4.0,
            "microservices": 4.0, "infrastructure": 4.0, "critical": 4.0
        }
    
    def _initialize_pattern_weights(self) -> Dict[str, float]:
        """Initialize pattern weights for complexity scoring."""
        return {
            "multiple_components": 2.0,
            "database_changes": 2.5,
            "api_integration": 3.0,
            "security_requirements": 3.5,
            "performance_requirements": 3.0,
            "user_interface": 2.0,
            "backend_logic": 2.5,
            "testing_required": 1.5,
            "documentation_required": 1.0
        }
    
    def detect_complexity(self, 
                         description: str, 
                         context: Optional[Dict[str, Any]] = None) -> int:
        """
        Detect complexity level from description and context.
        
        Args:
            description: Task or feature description
            context: Optional context information
        
        Returns:
            Complexity level (1-4)
        """
        result = self.analyze_complexity(description, context)
        return result.level
    
    def analyze_complexity(self, 
                          description: str, 
                          context: Optional[Dict[str, Any]] = None) -> ComplexityResult:
        """
        Comprehensive complexity analysis with detailed reasoning.
        
        Args:
            description: Task or feature description
            context: Optional context information
        
        Returns:
            ComplexityResult with level, confidence, and reasoning
        """
        if not description:
            return ComplexityResult(
                level=1,
                confidence=0.0,
                indicators=[],
                reasoning="No description provided, defaulting to Level 1"
            )
        
        # Analyze description
        description_analysis = self._analyze_description(description)
        
        # Analyze context if provided
        context_analysis = self._analyze_context(context) if context else {}
        
        # Combine analyses
        combined_score = self._combine_analyses(description_analysis, context_analysis)
        
        # Determine complexity level
        level = self._determine_complexity_level(combined_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(combined_score, level)
        
        # Generate indicators and reasoning
        indicators = self._generate_indicators(description_analysis, context_analysis)
        reasoning = self._generate_reasoning(level, indicators, combined_score)
        
        return ComplexityResult(
            level=level,
            confidence=confidence,
            indicators=indicators,
            reasoning=reasoning
        )
    
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze task description for complexity indicators."""
        description_lower = description.lower()
        
        analysis = {
            "keyword_scores": {},
            "pattern_matches": [],
            "length_score": 0,
            "technical_terms": 0,
            "complexity_phrases": 0
        }
        
        # Analyze keywords
        for keyword, weight in self.keyword_weights.items():
            if keyword in description_lower:
                analysis["keyword_scores"][keyword] = weight
        
        # Analyze patterns
        for level, indicators in self.complexity_indicators.items():
            for pattern in indicators.patterns:
                matches = re.findall(pattern, description_lower)
                if matches:
                    analysis["pattern_matches"].extend(matches)
        
        # Analyze length and structure
        analysis["length_score"] = min(len(description.split()) / 10, 4.0)
        
        # Count technical terms
        technical_terms = [
            "api", "database", "server", "client", "framework", "library",
            "algorithm", "architecture", "integration", "authentication",
            "authorization", "encryption", "deployment", "configuration"
        ]
        analysis["technical_terms"] = sum(1 for term in technical_terms if term in description_lower)
        
        # Count complexity phrases
        complexity_phrases = [
            "multiple", "several", "various", "complex", "advanced",
            "comprehensive", "detailed", "thorough", "extensive"
        ]
        analysis["complexity_phrases"] = sum(1 for phrase in complexity_phrases if phrase in description_lower)
        
        return analysis
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context information for complexity indicators."""
        analysis = {
            "estimated_effort": 0,
            "dependencies": 0,
            "affected_files": 0,
            "team_size": 0,
            "deadline_pressure": 0
        }
        
        # Analyze estimated effort
        effort = context.get("estimated_effort", "")
        if "hours" in effort.lower():
            analysis["estimated_effort"] = 1.0
        elif "days" in effort.lower():
            analysis["estimated_effort"] = 2.0
        elif "weeks" in effort.lower():
            analysis["estimated_effort"] = 3.0
        elif "months" in effort.lower():
            analysis["estimated_effort"] = 4.0
        
        # Analyze dependencies
        dependencies = context.get("dependencies", [])
        if isinstance(dependencies, list):
            analysis["dependencies"] = min(len(dependencies) / 2, 3.0)
        elif isinstance(dependencies, str) and dependencies.strip():
            analysis["dependencies"] = 1.0
        
        # Analyze affected files
        affected_files = context.get("affected_files", 0)
        if isinstance(affected_files, int):
            analysis["affected_files"] = min(affected_files / 5, 3.0)
        
        # Analyze team size
        team_size = context.get("team_size", 1)
        if isinstance(team_size, int):
            analysis["team_size"] = min(team_size / 3, 2.0)
        
        # Analyze deadline pressure
        deadline = context.get("deadline", "")
        if deadline:
            if "urgent" in deadline.lower() or "asap" in deadline.lower():
                analysis["deadline_pressure"] = 1.0
            elif "soon" in deadline.lower():
                analysis["deadline_pressure"] = 0.5
        
        return analysis
    
    def _combine_analyses(self, 
                         description_analysis: Dict[str, Any], 
                         context_analysis: Dict[str, Any]) -> Dict[int, float]:
        """Combine description and context analyses into complexity scores."""
        scores = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        
        # Add keyword scores
        for keyword, weight in description_analysis["keyword_scores"].items():
            if weight <= 1.0:
                scores[1] += weight
            elif weight <= 2.0:
                scores[2] += weight
            elif weight <= 3.0:
                scores[3] += weight
            else:
                scores[4] += weight
        
        # Add pattern match scores
        for match in description_analysis["pattern_matches"]:
            # Determine pattern complexity based on match content
            if any(word in match for word in ["fix", "update", "change"]):
                scores[1] += 1.0
            elif any(word in match for word in ["enhance", "improve", "add"]):
                scores[2] += 2.0
            elif any(word in match for word in ["implement", "develop", "create"]):
                scores[3] += 3.0
            elif any(word in match for word in ["architecture", "system", "platform"]):
                scores[4] += 4.0
        
        # Add length and complexity scores
        length_score = description_analysis["length_score"]
        if length_score <= 1.0:
            scores[1] += length_score
        elif length_score <= 2.0:
            scores[2] += length_score
        elif length_score <= 3.0:
            scores[3] += length_score
        else:
            scores[4] += length_score
        
        # Add technical terms score
        tech_terms = description_analysis["technical_terms"]
        scores[3] += min(tech_terms * 0.5, 2.0)
        
        # Add context scores
        if context_analysis:
            effort = context_analysis["estimated_effort"]
            scores[int(effort)] += effort
            
            dependencies = context_analysis["dependencies"]
            scores[2] += dependencies * 0.5
            
            affected_files = context_analysis["affected_files"]
            scores[3] += affected_files * 0.3
        
        return scores
    
    def _determine_complexity_level(self, scores: Dict[int, float]) -> int:
        """Determine complexity level from combined scores."""
        # Find the level with the highest score
        max_score = max(scores.values())
        if max_score == 0:
            return 1  # Default to Level 1
        
        # Return the level with the highest score
        for level in sorted(scores.keys(), reverse=True):
            if scores[level] == max_score:
                return level
        
        return 1  # Fallback
    
    def _calculate_confidence(self, scores: Dict[int, float], level: int) -> float:
        """Calculate confidence in the complexity level determination."""
        max_score = max(scores.values())
        total_score = sum(scores.values())
        
        if total_score == 0:
            return 0.0
        
        # Confidence is based on how much the winning level dominates
        confidence = max_score / total_score
        
        # Boost confidence if there's a clear winner
        second_highest = sorted(scores.values(), reverse=True)[1]
        if max_score > second_highest * 1.5:
            confidence = min(confidence * 1.2, 1.0)
        
        return confidence
    
    def _generate_indicators(self, 
                           description_analysis: Dict[str, Any], 
                           context_analysis: Dict[str, Any]) -> List[str]:
        """Generate list of complexity indicators found."""
        indicators = []
        
        # Add keyword indicators
        for keyword in description_analysis["keyword_scores"].keys():
            indicators.append(f"Keyword: '{keyword}'")
        
        # Add pattern indicators
        for match in description_analysis["pattern_matches"]:
            indicators.append(f"Pattern: '{match}'")
        
        # Add technical indicators
        if description_analysis["technical_terms"] > 0:
            indicators.append(f"Technical terms: {description_analysis['technical_terms']}")
        
        # Add context indicators
        if context_analysis:
            if context_analysis["estimated_effort"] > 0:
                indicators.append(f"Estimated effort: {context_analysis['estimated_effort']}")
            
            if context_analysis["dependencies"] > 0:
                indicators.append(f"Dependencies: {context_analysis['dependencies']}")
        
        return indicators
    
    def _generate_reasoning(self, 
                          level: int, 
                          indicators: List[str], 
                          scores: Dict[int, float]) -> str:
        """Generate human-readable reasoning for complexity level."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Complexity Level {level} detected based on:")
        
        # Add score breakdown
        for lvl in sorted(scores.keys()):
            if scores[lvl] > 0:
                reasoning_parts.append(f"  Level {lvl}: {scores[lvl]:.1f} points")
        
        # Add key indicators
        if indicators:
            reasoning_parts.append("Key indicators:")
            for indicator in indicators[:5]:  # Limit to top 5
                reasoning_parts.append(f"  - {indicator}")
        
        return "\n".join(reasoning_parts)
