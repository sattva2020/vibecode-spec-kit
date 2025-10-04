// Main Monitoring Service Entry Point
export { MonitoringService } from "./core/MonitoringService";
export { MetricsCollector } from "./core/MetricsCollector";
export * from "./types/MonitoringTypes";

// Main Monitoring Service class for easy integration
import { MonitoringService } from "./core/MonitoringService";
import { MonitoringConfig } from "./types/MonitoringTypes";

export class MemoryBankMonitoringService {
  private monitoringService: MonitoringService;
  
  constructor(config?: Partial<MonitoringConfig>) {
    const defaultConfig: MonitoringConfig = {
      collectionInterval: 5000, // 5 seconds
      retentionPeriod: 30, // 30 days
      alertChannels: [],
      metricsEndpoint: "/metrics",
      grafanaUrl: "http://localhost:3000",
      prometheusUrl: "http://localhost:9090",
      ...config
    };

    this.monitoringService = new MonitoringService(defaultConfig);
  }

  // Initialize monitoring service
  async initialize(): Promise<void> {
    console.log("📊 Initializing Memory Bank Monitoring Service...");
    await this.monitoringService.start();
    console.log("✅ Monitoring Service initialized successfully");
  }

  // Start monitoring
  async start(): Promise<void> {
    return await this.monitoringService.start();
  }

  // Stop monitoring
  async stop(): Promise<void> {
    return await this.monitoringService.stop();
  }

  // Get monitoring status
  getStatus() {
    return this.monitoringService.getStatus();
  }

  // Get metrics
  getMetrics() {
    return this.monitoringService.getMetrics();
  }

  // Get Prometheus metrics
  async getPrometheusMetrics() {
    return await this.monitoringService.getPrometheusMetrics();
  }

  // Get alerts
  getAlerts() {
    return this.monitoringService.getAlerts();
  }

  // Get active alerts
  getActiveAlerts() {
    return this.monitoringService.getActiveAlerts();
  }

  // Health check
  async healthCheck() {
    return await this.monitoringService.healthCheck();
  }

  // Event handling
  on(event: string, listener: (...args: any[]) => void) {
    this.monitoringService.on(event, listener);
  }

  off(event: string, listener: (...args: any[]) => void) {
    this.monitoringService.off(event, listener);
  }

  emit(event: string, ...args: any[]) {
    this.monitoringService.emit(event, ...args);
  }
}

// Default export
export default MemoryBankMonitoringService;
