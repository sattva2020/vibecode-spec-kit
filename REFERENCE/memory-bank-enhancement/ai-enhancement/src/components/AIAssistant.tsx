// AI Assistant React Component
import React, { useState, useEffect } from "react";
import { AIEngine } from "../core/AIEngine";
import { AISuggestion, SuggestionType, SuggestionPriority, AIAnalytics, Insight } from "../types/AITypes";

interface AIAssistantProps {
  isVisible: boolean;
  onToggle: () => void;
  mode: string;
  context?: any;
}

export const AIAssistant: React.FC<AIAssistantProps> = ({ isVisible, onToggle, mode, context }) => {
  const [aiEngine] = useState(() => new AIEngine({
    enablePredictions: true,
    enableSuggestions: true,
    enableLearning: true,
    modelUpdateInterval: 24,
    suggestionThreshold: 0.7,
    learningRate: 0.01,
    maxSuggestions: 5,
    contextWindow: 30
  }));
  
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [analytics, setAnalytics] = useState<AIAnalytics | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    initializeAI();
  }, []);

  useEffect(() => {
    if (isInitialized && context) {
      generateSuggestions();
    }
  }, [isInitialized, mode, context]);

  const initializeAI = async () => {
    try {
      await aiEngine.initialize();
      setIsInitialized(true);
      
      // Set up event listeners
      aiEngine.on("suggestionsGenerated", (newSuggestions: AISuggestion[]) => {
        setSuggestions(newSuggestions);
      });
      
      aiEngine.on("aiEngineInitialized", () => {
        console.log("AI Engine initialized successfully");
      });
      
    } catch (error) {
      console.error("Failed to initialize AI Engine:", error);
    }
  };

  const generateSuggestions = async () => {
    if (!isInitialized) return;
    
    setIsLoading(true);
    try {
      const newSuggestions = await aiEngine.generateSuggestions({
        mode,
        taskType: context?.taskType,
        userBehavior: context?.userBehavior,
        systemMetrics: context?.systemMetrics,
        codeContext: context?.codeContext
      });
      
      setSuggestions(newSuggestions);
      setAnalytics(aiEngine.getAnalytics());
      setInsights(aiEngine.getAnalytics().insights);
    } catch (error) {
      console.error("Failed to generate suggestions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (suggestionId: string, rating: number, helpful: boolean, comments?: string) => {
    try {
      await aiEngine.recordFeedback(suggestionId, {
        rating,
        helpful,
        comments,
        timestamp: new Date()
      });
      
      // Remove the suggestion after feedback
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
    } catch (error) {
      console.error("Failed to record feedback:", error);
    }
  };

  const getPriorityColor = (priority: SuggestionPriority): string => {
    switch (priority) {
      case SuggestionPriority.CRITICAL: return "text-red-600 bg-red-100";
      case SuggestionPriority.HIGH: return "text-orange-600 bg-orange-100";
      case SuggestionPriority.MEDIUM: return "text-yellow-600 bg-yellow-100";
      case SuggestionPriority.LOW: return "text-blue-600 bg-blue-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const getTypeIcon = (type: SuggestionType): string => {
    switch (type) {
      case SuggestionType.OPTIMIZATION: return "⚡";
      case SuggestionType.SECURITY: return "🔒";
      case SuggestionType.PERFORMANCE: return "📊";
      case SuggestionType.WORKFLOW: return "🔄";
      case SuggestionType.CODE_QUALITY: return "💻";
      default: return "💡";
    }
  };

  if (!isVisible) {
    return (
      <button
        onClick={onToggle}
        className="fixed top-20 right-4 z-50 bg-purple-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-purple-700 transition-colors"
      >
        🤖 AI Assistant
      </button>
    );
  }

  return (
    <div className="fixed top-0 right-0 w-96 h-full bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-blue-50">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
          <button
            onClick={onToggle}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">Mode: {mode}</p>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* AI Status */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <span className="text-green-600">🤖</span>
            <span className="text-sm font-medium text-green-900">AI Engine Active</span>
          </div>
          <p className="text-xs text-green-700 mt-1">
            {analytics ? `${Math.round(analytics.accuracyRate * 100)}% accuracy` : "Initializing..."}
          </p>
        </div>

        {/* Suggestions */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-gray-900">Smart Suggestions</h3>
            {isLoading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
            )}
          </div>
          
          {suggestions.length === 0 && !isLoading ? (
            <div className="text-center py-4 text-gray-500">
              <span className="text-2xl">💡</span>
              <p className="text-sm mt-1">No suggestions available</p>
            </div>
          ) : (
            suggestions.map((suggestion) => (
              <div key={suggestion.id} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getTypeIcon(suggestion.type)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(suggestion.priority)}`}>
                      {suggestion.priority.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {Math.round(suggestion.confidence * 100)}%
                  </span>
                </div>
                
                <h4 className="font-medium text-gray-900 mb-1">{suggestion.title}</h4>
                <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                <p className="text-xs text-blue-600 mb-3">💡 {suggestion.action}</p>
                
                {/* Feedback */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleFeedback(suggestion.id, 5, true)}
                    className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200 transition-colors"
                  >
                    👍 Helpful
                  </button>
                  <button
                    onClick={() => handleFeedback(suggestion.id, 2, false)}
                    className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200 transition-colors"
                  >
                    👎 Not Helpful
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Insights */}
        {insights.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-medium text-gray-900">AI Insights</h3>
            {insights.map((insight) => (
              <div key={insight.id} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium text-blue-900">{insight.title}</h4>
                  <span className="text-xs text-blue-600">
                    {Math.round(insight.confidence * 100)}%
                  </span>
                </div>
                <p className="text-sm text-blue-700">{insight.description}</p>
                <div className="mt-2">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                    insight.impact === "high" ? "bg-red-100 text-red-700" :
                    insight.impact === "medium" ? "bg-yellow-100 text-yellow-700" :
                    "bg-green-100 text-green-700"
                  }`}>
                    {insight.impact.toUpperCase()} IMPACT
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Analytics */}
        {analytics && (
          <div className="space-y-2">
            <h3 className="font-medium text-gray-900">AI Analytics</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600">Accuracy</div>
                <div className="font-medium">{Math.round(analytics.accuracyRate * 100)}%</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600">Adoption</div>
                <div className="font-medium">{Math.round(analytics.suggestionAdoption * 100)}%</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600">Satisfaction</div>
                <div className="font-medium">{Math.round(analytics.userSatisfaction * 100)}%</div>
              </div>
              <div className="bg-gray-50 p-2 rounded">
                <div className="text-gray-600">Learning</div>
                <div className="font-medium">{Math.round(analytics.learningProgress * 100)}%</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistant;
