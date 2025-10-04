// Main AI Enhancement Entry Point
export { AIEngine } from "./core/AIEngine";
export { AIAssistant } from "./components/AIAssistant";
export * from "./types/AITypes";

// Main AI Enhancement class for easy integration
import { AIEngine } from "./core/AIEngine";
import { AIEngineConfig } from "./types/AITypes";

export class MemoryBankAIEnhancement {
  private aiEngine: AIEngine;
  
  constructor(config?: Partial<AIEngineConfig>) {
    const defaultConfig: AIEngineConfig = {
      enablePredictions: true,
      enableSuggestions: true,
      enableLearning: true,
      modelUpdateInterval: 24, // 24 hours
      suggestionThreshold: 0.7,
      learningRate: 0.01,
      maxSuggestions: 5,
      contextWindow: 30, // 30 minutes
      ...config
    };

    this.aiEngine = new AIEngine(defaultConfig);
  }

  // Initialize AI enhancement
  async initialize(): Promise<void> {
    console.log("🤖 Initializing Memory Bank AI Enhancement...");
    await this.aiEngine.initialize();
    console.log("✅ AI Enhancement initialized successfully");
  }

  // Get AI engine
  getAIEngine() {
    return this.aiEngine;
  }

  // Generate suggestions
  async generateSuggestions(context: any) {
    return await this.aiEngine.generateSuggestions(context);
  }

  // Make predictions
  async predictPerformance(context: any) {
    return await this.aiEngine.predictPerformance(context);
  }

  // Record feedback
  async recordFeedback(suggestionId: string, feedback: any) {
    return await this.aiEngine.recordFeedback(suggestionId, feedback);
  }

  // Get analytics
  getAnalytics() {
    return this.aiEngine.getAnalytics();
  }

  // Event handling
  on(event: string, listener: (...args: any[]) => void) {
    this.aiEngine.on(event, listener);
  }

  off(event: string, listener: (...args: any[]) => void) {
    this.aiEngine.off(event, listener);
  }

  emit(event: string, ...args: any[]) {
    this.aiEngine.emit(event, ...args);
  }
}

// Default export
export default MemoryBankAIEnhancement;
