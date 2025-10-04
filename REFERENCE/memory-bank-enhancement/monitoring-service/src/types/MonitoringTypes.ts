// Monitoring Service Types
export interface SystemMetrics {
  cpu: CPUMetrics;
  memory: MemoryMetrics;
  disk: DiskMetrics;
  network: NetworkMetrics;
  timestamp: Date;
}

export interface CPUMetrics {
  usage: number; // percentage
  loadAverage: number[];
  cores: number;
  temperature?: number;
}

export interface MemoryMetrics {
  total: number; // bytes
  used: number; // bytes
  free: number; // bytes
  usage: number; // percentage
  swap: {
    total: number;
    used: number;
    free: number;
  };
}

export interface DiskMetrics {
  total: number; // bytes
  used: number; // bytes
  free: number; // bytes
  usage: number; // percentage
  readSpeed: number; // bytes per second
  writeSpeed: number; // bytes per second
}

export interface NetworkMetrics {
  bytesReceived: number;
  bytesSent: number;
  packetsReceived: number;
  packetsSent: number;
  connections: number;
}

export interface ApplicationMetrics {
  requests: RequestMetrics;
  errors: ErrorMetrics;
  performance: PerformanceMetrics;
  users: UserMetrics;
  timestamp: Date;
}

export interface RequestMetrics {
  total: number;
  successful: number;
  failed: number;
  averageResponseTime: number; // milliseconds
  requestsPerSecond: number;
}

export interface ErrorMetrics {
  total: number;
  errorsPerSecond: number;
  errorRate: number; // percentage
  errorTypes: Record<string, number>;
}

export interface PerformanceMetrics {
  responseTime: {
    min: number;
    max: number;
    average: number;
    p95: number;
    p99: number;
  };
  throughput: number; // requests per second
  uptime: number; // seconds
}

export interface UserMetrics {
  active: number;
  total: number;
  newUsers: number;
  sessionDuration: number; // average in minutes
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source: string;
  timestamp: Date;
  resolvedAt?: Date;
  acknowledgedBy?: string;
  acknowledgedAt?: Date;
}

export enum AlertSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum AlertStatus {
  ACTIVE = "active",
  ACKNOWLEDGED = "acknowledged",
  RESOLVED = "resolved",
  SUPPRESSED = "suppressed"
}

export interface AlertRule {
  id: string;
  name: string;
  description: string;
  condition: string;
  severity: AlertSeverity;
  enabled: boolean;
  cooldown: number; // seconds
  lastTriggered?: Date;
}

export interface MonitoringConfig {
  collectionInterval: number; // milliseconds
  retentionPeriod: number; // days
  alertChannels: AlertChannel[];
  metricsEndpoint: string;
  grafanaUrl: string;
  prometheusUrl: string;
}

export interface AlertChannel {
  id: string;
  name: string;
  type: "email" | "slack" | "webhook" | "sms";
  config: Record<string, any>;
  enabled: boolean;
}

export interface DashboardConfig {
  id: string;
  name: string;
  description: string;
  panels: PanelConfig[];
  refreshInterval: number; // seconds
  timeRange: {
    from: string;
    to: string;
  };
}

export interface PanelConfig {
  id: string;
  title: string;
  type: "graph" | "singlestat" | "table" | "heatmap";
  targets: PanelTarget[];
  options: Record<string, any>;
}

export interface PanelTarget {
  expr: string;
  legendFormat?: string;
  refId: string;
}

export interface MonitoringStatus {
  isCollecting: boolean;
  lastCollection: Date;
  metricsCount: number;
  alertCount: number;
  uptime: number; // seconds
  version: string;
}
