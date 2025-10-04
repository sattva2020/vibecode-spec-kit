// Monitoring Service Core
import { MetricsCollector } from "./MetricsCollector";
import { MonitoringStatus, MonitoringConfig, Alert, AlertRule, AlertSeverity, AlertStatus } from "../types/MonitoringTypes";
import { EventEmitter } from "events";

export class MonitoringService extends EventEmitter {
  private metricsCollector: MetricsCollector;
  private status: MonitoringStatus;
  private config: MonitoringConfig;
  private alerts: Alert[] = [];
  private alertRules: AlertRule[] = [];
  private isRunning: boolean = false;
  private collectionInterval: NodeJS.Timeout | null = null;

  constructor(config: MonitoringConfig) {
    super();
    this.config = config;
    this.metricsCollector = new MetricsCollector();
    this.status = this.initializeStatus();
    this.initializeDefaultAlertRules();
  }

  private initializeStatus(): MonitoringStatus {
    return {
      isCollecting: false,
      lastCollection: new Date(),
      metricsCount: 0,
      alertCount: 0,
      uptime: 0,
      version: "1.0.0"
    };
  }

  private initializeDefaultAlertRules(): void {
    this.alertRules = [
      {
        id: "high-cpu-usage",
        name: "High CPU Usage",
        description: "Alert when CPU usage exceeds 80%",
        condition: "cpu_usage > 80",
        severity: AlertSeverity.HIGH,
        enabled: true,
        cooldown: 300 // 5 minutes
      },
      {
        id: "high-memory-usage",
        name: "High Memory Usage",
        description: "Alert when memory usage exceeds 85%",
        condition: "memory_usage > 85",
        severity: AlertSeverity.HIGH,
        enabled: true,
        cooldown: 300
      },
      {
        id: "high-error-rate",
        name: "High Error Rate",
        description: "Alert when error rate exceeds 5%",
        condition: "error_rate > 5",
        severity: AlertSeverity.CRITICAL,
        enabled: true,
        cooldown: 60 // 1 minute
      },
      {
        id: "slow-response-time",
        name: "Slow Response Time",
        description: "Alert when average response time exceeds 2 seconds",
        condition: "response_time > 2000",
        severity: AlertSeverity.MEDIUM,
        enabled: true,
        cooldown: 180 // 3 minutes
      }
    ];
  }

  async start(): Promise<void> {
    if (this.isRunning) {
      console.log("⚠️ Monitoring service is already running");
      return;
    }

    console.log("🚀 Starting Memory Bank Monitoring Service...");
    
    this.isRunning = true;
    this.status.isCollecting = true;
    this.status.uptime = Date.now();

    // Start metrics collection
    await this.startMetricsCollection();

    // Start alert evaluation
    this.startAlertEvaluation();

    console.log("✅ Monitoring service started successfully");
    this.emit("serviceStarted", this.status);
  }

  async stop(): Promise<void> {
    if (!this.isRunning) {
      console.log("⚠️ Monitoring service is not running");
      return;
    }

    console.log("🛑 Stopping Memory Bank Monitoring Service...");
    
    this.isRunning = false;
    this.status.isCollecting = false;

    if (this.collectionInterval) {
      clearInterval(this.collectionInterval);
      this.collectionInterval = null;
    }

    console.log("✅ Monitoring service stopped successfully");
    this.emit("serviceStopped", this.status);
  }

  private async startMetricsCollection(): Promise<void> {
    // Initial collection
    await this.collectMetrics();

    // Set up interval collection
    this.collectionInterval = setInterval(async () => {
      await this.collectMetrics();
    }, this.config.collectionInterval);
  }

  private async collectMetrics(): Promise<void> {
    try {
      // Collect system metrics
      const systemMetrics = await this.metricsCollector.collectSystemMetrics();
      
      // Collect application metrics
      const applicationMetrics = await this.metricsCollector.collectApplicationMetrics();

      // Update status
      this.status.lastCollection = new Date();
      this.status.metricsCount += 2; // system + application
      this.status.uptime = Date.now() - this.status.uptime;

      // Emit metrics collected event
      this.emit("metricsCollected", {
        system: systemMetrics,
        application: applicationMetrics
      });

      // Evaluate alert rules
      await this.evaluateAlertRules(systemMetrics, applicationMetrics);

    } catch (error) {
      console.error("❌ Error collecting metrics:", error);
      this.emit("error", error);
    }
  }

  private async evaluateAlertRules(systemMetrics: any, applicationMetrics: any): Promise<void> {
    for (const rule of this.alertRules) {
      if (!rule.enabled) continue;

      // Check cooldown
      if (rule.lastTriggered && 
          Date.now() - rule.lastTriggered.getTime() < rule.cooldown * 1000) {
        continue;
      }

      const shouldTrigger = await this.evaluateAlertCondition(rule, systemMetrics, applicationMetrics);
      
      if (shouldTrigger) {
        await this.triggerAlert(rule, systemMetrics, applicationMetrics);
        rule.lastTriggered = new Date();
      }
    }
  }

  private async evaluateAlertCondition(rule: AlertRule, systemMetrics: any, applicationMetrics: any): Promise<boolean> {
    // Simple condition evaluation - in real implementation would use a proper expression evaluator
    try {
      switch (rule.id) {
        case "high-cpu-usage":
          return systemMetrics.cpu.usage > 80;
        case "high-memory-usage":
          return systemMetrics.memory.usage > 85;
        case "high-error-rate":
          return applicationMetrics.errors.errorRate > 5;
        case "slow-response-time":
          return applicationMetrics.performance.responseTime.average > 2000;
        default:
          return false;
      }
    } catch (error) {
      console.error(`Error evaluating alert rule ${rule.id}:`, error);
      return false;
    }
  }

  private async triggerAlert(rule: AlertRule, systemMetrics: any, applicationMetrics: any): Promise<void> {
    const alert: Alert = {
      id: `alert-${rule.id}-${Date.now()}`,
      title: rule.name,
      description: rule.description,
      severity: rule.severity,
      status: AlertStatus.ACTIVE,
      source: "monitoring-service",
      timestamp: new Date()
    };

    this.alerts.push(alert);
    this.status.alertCount = this.alerts.filter(a => a.status === AlertStatus.ACTIVE).length;

    console.log(`🚨 Alert triggered: ${alert.title} (${alert.severity})`);
    this.emit("alertTriggered", alert);
  }

  private startAlertEvaluation(): void {
    // Alert evaluation is handled in collectMetrics
    // This method can be extended for more complex alert evaluation logic
  }

  // Public methods
  getStatus(): MonitoringStatus {
    return { ...this.status };
  }

  getMetrics() {
    return this.metricsCollector.getAllMetrics();
  }

  async getPrometheusMetrics(): Promise<string> {
    return await this.metricsCollector.getPrometheusMetrics();
  }

  getAlerts(): Alert[] {
    return [...this.alerts];
  }

  getActiveAlerts(): Alert[] {
    return this.alerts.filter(alert => alert.status === AlertStatus.ACTIVE);
  }

  async acknowledgeAlert(alertId: string, acknowledgedBy: string): Promise<boolean> {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.status = AlertStatus.ACKNOWLEDGED;
      alert.acknowledgedBy = acknowledgedBy;
      alert.acknowledgedAt = new Date();
      this.emit("alertAcknowledged", alert);
      return true;
    }
    return false;
  }

  async resolveAlert(alertId: string): Promise<boolean> {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.status = AlertStatus.RESOLVED;
      alert.resolvedAt = new Date();
      this.emit("alertResolved", alert);
      return true;
    }
    return false;
  }

  addAlertRule(rule: AlertRule): void {
    this.alertRules.push(rule);
    this.emit("alertRuleAdded", rule);
  }

  updateAlertRule(ruleId: string, updates: Partial<AlertRule>): void {
    const ruleIndex = this.alertRules.findIndex(rule => rule.id === ruleId);
    if (ruleIndex !== -1) {
      this.alertRules[ruleIndex] = { ...this.alertRules[ruleIndex], ...updates };
      this.emit("alertRuleUpdated", this.alertRules[ruleIndex]);
    }
  }

  removeAlertRule(ruleId: string): void {
    this.alertRules = this.alertRules.filter(rule => rule.id !== ruleId);
    this.emit("alertRuleRemoved", ruleId);
  }

  getAlertRules(): AlertRule[] {
    return [...this.alertRules];
  }

  // Health check
  async healthCheck(): Promise<{ status: string; details: any }> {
    const metrics = this.metricsCollector.getAllMetrics();
    const activeAlerts = this.getActiveAlerts();
    
    return {
      status: this.isRunning ? "healthy" : "stopped",
      details: {
        isRunning: this.isRunning,
        metricsCollected: this.status.metricsCount,
        activeAlerts: activeAlerts.length,
        uptime: this.status.uptime,
        lastCollection: this.status.lastCollection
      }
    };
  }
}
