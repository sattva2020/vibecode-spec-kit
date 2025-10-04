// AI Enhancement Types
export interface AIPrediction {
  id: string;
  type: PredictionType;
  confidence: number; // 0-1
  value: number;
  timestamp: Date;
  context: PredictionContext;
  recommendations: string[];
}

export enum PredictionType {
  PERFORMANCE = "performance",
  ERROR_RATE = "error_rate",
  USER_BEHAVIOR = "user_behavior",
  RESOURCE_USAGE = "resource_usage",
  SECURITY_RISK = "security_risk"
}

export interface PredictionContext {
  userId?: string;
  sessionId?: string;
  mode: string;
  taskType?: string;
  systemState: SystemState;
}

export interface SystemState {
  cpuUsage: number;
  memoryUsage: number;
  activeUsers: number;
  errorRate: number;
  responseTime: number;
}

export interface AISuggestion {
  id: string;
  type: SuggestionType;
  priority: SuggestionPriority;
  title: string;
  description: string;
  action: string;
  confidence: number; // 0-1
  context: SuggestionContext;
  feedback?: UserFeedback;
  timestamp: Date;
}

export enum SuggestionType {
  OPTIMIZATION = "optimization",
  SECURITY = "security",
  PERFORMANCE = "performance",
  WORKFLOW = "workflow",
  CODE_QUALITY = "code_quality"
}

export enum SuggestionPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export interface SuggestionContext {
  mode: string;
  taskType?: string;
  userBehavior?: UserBehavior;
  systemMetrics?: SystemMetrics;
  codeContext?: CodeContext;
}

export interface UserBehavior {
  patterns: string[];
  preferences: string[];
  efficiency: number;
  errors: number;
}

export interface SystemMetrics {
  performance: number;
  stability: number;
  resourceUsage: number;
  errorRate: number;
}

export interface CodeContext {
  language: string;
  complexity: number;
  quality: number;
  patterns: string[];
  issues: CodeIssue[];
}

export interface CodeIssue {
  type: string;
  severity: string;
  line: number;
  description: string;
  suggestion: string;
}

export interface UserFeedback {
  rating: number; // 1-5
  helpful: boolean;
  comments?: string;
  timestamp: Date;
}

export interface LearningData {
  userId: string;
  suggestions: AISuggestion[];
  feedback: UserFeedback[];
  outcomes: Outcome[];
  patterns: BehaviorPattern[];
}

export interface Outcome {
  suggestionId: string;
  actionTaken: string;
  result: string;
  success: boolean;
  timestamp: Date;
}

export interface BehaviorPattern {
  pattern: string;
  frequency: number;
  success: number;
  context: string;
}

export interface AIAnalytics {
  totalPredictions: number;
  accuracyRate: number;
  suggestionAdoption: number;
  userSatisfaction: number;
  learningProgress: number;
  insights: Insight[];
}

export interface Insight {
  id: string;
  type: InsightType;
  title: string;
  description: string;
  confidence: number;
  impact: string;
  recommendations: string[];
  timestamp: Date;
}

export enum InsightType {
  PERFORMANCE_TREND = "performance_trend",
  USER_BEHAVIOR = "user_behavior",
  SYSTEM_OPTIMIZATION = "system_optimization",
  SECURITY_ANALYSIS = "security_analysis",
  WORKFLOW_EFFICIENCY = "workflow_efficiency"
}

export interface AIModel {
  id: string;
  name: string;
  type: ModelType;
  version: string;
  accuracy: number;
  lastTrained: Date;
  status: ModelStatus;
  parameters: ModelParameters;
}

export enum ModelType {
  PREDICTION = "prediction",
  CLASSIFICATION = "classification",
  CLUSTERING = "clustering",
  RECOMMENDATION = "recommendation"
}

export enum ModelStatus {
  TRAINING = "training",
  READY = "ready",
  ERROR = "error",
  DEPRECATED = "deprecated"
}

export interface ModelParameters {
  learningRate: number;
  epochs: number;
  batchSize: number;
  layers: number[];
  activation: string;
}

export interface AIEngineConfig {
  enablePredictions: boolean;
  enableSuggestions: boolean;
  enableLearning: boolean;
  modelUpdateInterval: number; // hours
  suggestionThreshold: number; // confidence threshold
  learningRate: number;
  maxSuggestions: number;
  contextWindow: number; // minutes
}

export interface AISession {
  id: string;
  userId: string;
  startTime: Date;
  endTime?: Date;
  interactions: Interaction[];
  context: SessionContext;
  insights: Insight[];
}

export interface Interaction {
  id: string;
  type: InteractionType;
  input: string;
  output: string;
  timestamp: Date;
  feedback?: UserFeedback;
}

export enum InteractionType {
  SUGGESTION = "suggestion",
  PREDICTION = "prediction",
  ANALYSIS = "analysis",
  RECOMMENDATION = "recommendation"
}

export interface SessionContext {
  mode: string;
  taskType?: string;
  systemState: SystemState;
  userPreferences: string[];
  recentActions: string[];
}
