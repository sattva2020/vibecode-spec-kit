// Metrics Collector Service
import { SystemMetrics, ApplicationMetrics, CPUMetrics, MemoryMetrics, DiskMetrics, NetworkMetrics } from "../types/MonitoringTypes";
import * as os from "os";
import * as fs from "fs";
import * as prometheus from "prom-client";

export class MetricsCollector {
  private metrics: {
    system: SystemMetrics | null;
    application: ApplicationMetrics | null;
  } = {
    system: null,
    application: null
  };

  private prometheusRegistry: prometheus.Registry;
  private metricsCollectors!: {
    cpuUsage: prometheus.Gauge;
    memoryUsage: prometheus.Gauge;
    diskUsage: prometheus.Gauge;
    networkBytes: prometheus.Counter;
    requestCount: prometheus.Counter;
    responseTime: prometheus.Histogram;
    errorCount: prometheus.Counter;
    activeUsers: prometheus.Gauge;
  };

  constructor() {
    this.prometheusRegistry = new prometheus.Registry();
    this.initializePrometheusMetrics();
  }

  private initializePrometheusMetrics(): void {
    // System metrics
    this.metricsCollectors = {
      cpuUsage: new prometheus.Gauge({
        name: "memory_bank_cpu_usage_percent",
        help: "CPU usage percentage",
        registers: [this.prometheusRegistry]
      }),
      memoryUsage: new prometheus.Gauge({
        name: "memory_bank_memory_usage_percent",
        help: "Memory usage percentage",
        registers: [this.prometheusRegistry]
      }),
      diskUsage: new prometheus.Gauge({
        name: "memory_bank_disk_usage_percent",
        help: "Disk usage percentage",
        registers: [this.prometheusRegistry]
      }),
      networkBytes: new prometheus.Counter({
        name: "memory_bank_network_bytes_total",
        help: "Total network bytes transferred",
        labelNames: ["direction"],
        registers: [this.prometheusRegistry]
      }),
      
      // Application metrics
      requestCount: new prometheus.Counter({
        name: "memory_bank_requests_total",
        help: "Total number of requests",
        labelNames: ["method", "status"],
        registers: [this.prometheusRegistry]
      }),
      responseTime: new prometheus.Histogram({
        name: "memory_bank_response_time_seconds",
        help: "Request response time in seconds",
        labelNames: ["method", "endpoint"],
        buckets: [0.1, 0.5, 1, 2, 5, 10],
        registers: [this.prometheusRegistry]
      }),
      errorCount: new prometheus.Counter({
        name: "memory_bank_errors_total",
        help: "Total number of errors",
        labelNames: ["type", "severity"],
        registers: [this.prometheusRegistry]
      }),
      activeUsers: new prometheus.Gauge({
        name: "memory_bank_active_users",
        help: "Number of active users",
        registers: [this.prometheusRegistry]
      })
    };
  }

  async collectSystemMetrics(): Promise<SystemMetrics> {
    const cpuUsage = await this.getCPUUsage();
    const memoryUsage = this.getMemoryUsage();
    const diskUsage = await this.getDiskUsage();
    const networkMetrics = this.getNetworkMetrics();

    const systemMetrics: SystemMetrics = {
      cpu: cpuUsage,
      memory: memoryUsage,
      disk: diskUsage,
      network: networkMetrics,
      timestamp: new Date()
    };

    // Update Prometheus metrics
    this.metricsCollectors.cpuUsage.set(cpuUsage.usage);
    this.metricsCollectors.memoryUsage.set(memoryUsage.usage);
    this.metricsCollectors.diskUsage.set(diskUsage.usage);

    this.metrics.system = systemMetrics;
    return systemMetrics;
  }

  async collectApplicationMetrics(): Promise<ApplicationMetrics> {
    // Simulate application metrics collection
    const requestMetrics = this.getRequestMetrics();
    const errorMetrics = this.getErrorMetrics();
    const performanceMetrics = this.getPerformanceMetrics();
    const userMetrics = this.getUserMetrics();

    const applicationMetrics: ApplicationMetrics = {
      requests: requestMetrics,
      errors: errorMetrics,
      performance: performanceMetrics,
      users: userMetrics,
      timestamp: new Date()
    };

    // Update Prometheus metrics
    this.metricsCollectors.activeUsers.set(userMetrics.active);

    this.metrics.application = applicationMetrics;
    return applicationMetrics;
  }

  private async getCPUUsage(): Promise<CPUMetrics> {
    const cpus = os.cpus();
    const loadAverage = os.loadavg();
    
    // Calculate CPU usage
    let totalIdle = 0;
    let totalTick = 0;
    
    cpus.forEach(cpu => {
      for (const type in cpu.times) {
        totalTick += cpu.times[type as keyof typeof cpu.times];
      }
      totalIdle += cpu.times.idle;
    });

    const usage = 100 - Math.round((totalIdle / totalTick) * 100);

    return {
      usage: Math.max(0, Math.min(100, usage)),
      loadAverage,
      cores: cpus.length
    };
  }

  private getMemoryUsage(): MemoryMetrics {
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;

    return {
      total: totalMemory,
      used: usedMemory,
      free: freeMemory,
      usage: Math.round((usedMemory / totalMemory) * 100),
      swap: {
        total: 0, // Not available on all systems
        used: 0,
        free: 0
      }
    };
  }

  private async getDiskUsage(): Promise<DiskMetrics> {
    try {
      const stats = await fs.promises.statfs("/");
      const total = stats.bavail * stats.bsize + stats.bfree * stats.bsize;
      const free = stats.bavail * stats.bsize;
      const used = total - free;

      return {
        total,
        used,
        free,
        usage: Math.round((used / total) * 100),
        readSpeed: 0, // Would need additional monitoring
        writeSpeed: 0
      };
    } catch (error) {
      // Fallback for Windows or if statfs is not available
      return {
        total: 1000000000000, // 1TB
        used: 500000000000,   // 500GB
        free: 500000000000,   // 500GB
        usage: 50,
        readSpeed: 0,
        writeSpeed: 0
      };
    }
  }

  private getNetworkMetrics(): NetworkMetrics {
    const networkInterfaces = os.networkInterfaces();
    let bytesReceived = 0;
    let bytesSent = 0;
    let packetsReceived = 0;
    let packetsSent = 0;

    // Simplified network metrics - in real implementation would track actual network usage
    return {
      bytesReceived,
      bytesSent,
      packetsReceived,
      packetsSent,
      connections: 0 // Would need additional monitoring
    };
  }

  private getRequestMetrics() {
    // Simulate request metrics
    return {
      total: 1250,
      successful: 1200,
      failed: 50,
      averageResponseTime: 245,
      requestsPerSecond: 15.5
    };
  }

  private getErrorMetrics() {
    // Simulate error metrics
    return {
      total: 50,
      errorsPerSecond: 0.8,
      errorRate: 4.0,
      errorTypes: {
        "validation": 20,
        "authentication": 15,
        "authorization": 10,
        "server": 5
      }
    };
  }

  private getPerformanceMetrics() {
    // Simulate performance metrics
    return {
      responseTime: {
        min: 50,
        max: 2000,
        average: 245,
        p95: 800,
        p99: 1200
      },
      throughput: 15.5,
      uptime: process.uptime()
    };
  }

  private getUserMetrics() {
    // Simulate user metrics
    return {
      active: 42,
      total: 1250,
      newUsers: 15,
      sessionDuration: 28.5
    };
  }

  // Prometheus integration
  async getPrometheusMetrics(): Promise<string> {
    return this.prometheusRegistry.metrics();
  }

  getPrometheusRegistry(): prometheus.Registry {
    return this.prometheusRegistry;
  }

  // Getters
  getSystemMetrics(): SystemMetrics | null {
    return this.metrics.system;
  }

  getApplicationMetrics(): ApplicationMetrics | null {
    return this.metrics.application;
  }

  getAllMetrics() {
    return this.metrics;
  }
}
