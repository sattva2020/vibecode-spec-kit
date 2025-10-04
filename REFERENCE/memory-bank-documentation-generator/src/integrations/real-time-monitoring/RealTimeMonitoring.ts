import { ProjectInfo } from "../../types/ProjectTypes";
import { RFCDocument } from "../../types/RFCTypes";

export interface MonitoringMetric {
    id: string;
    name: string;
    type: "counter" | "gauge" | "histogram" | "summary";
    value: number;
    labels: { [key: string]: string };
    timestamp: Date;
}

export interface MonitoringAlert {
    id: string;
    name: string;
    condition: AlertCondition;
    severity: "low" | "medium" | "high" | "critical";
    message: string;
    enabled: boolean;
    lastTriggered?: Date;
}

export interface AlertCondition {
    metricId: string;
    operator: "greater" | "less" | "equals" | "not_equals";
    threshold: number;
    duration: number; // в миллисекундах
}

export interface MonitoringEvent {
    id: string;
    type: "document-generated" | "diagram-updated" | "validation-failed" | "hook-executed" | "rule-triggered";
    data: any;
    timestamp: Date;
    severity: "info" | "warning" | "error" | "critical";
}

export interface MonitoringDashboard {
    id: string;
    name: string;
    widgets: DashboardWidget[];
    refreshInterval: number;
    lastUpdated: Date;
}

export interface DashboardWidget {
    id: string;
    type: "metric" | "chart" | "alert" | "log";
    title: string;
    data: any;
    position: { x: number; y: number; width: number; height: number };
}

export class RealTimeMonitoring {
    private metrics: Map<string, MonitoringMetric> = new Map();
    private alerts: Map<string, MonitoringAlert> = new Map();
    private events: MonitoringEvent[] = [];
    private dashboards: Map<string, MonitoringDashboard> = new Map();
    private isRunning: boolean = false;
    private updateInterval: NodeJS.Timeout | null = null;

    constructor() {
        this.initializeDefaultMetrics();
        this.initializeDefaultAlerts();
        this.initializeDefaultDashboards();
    }

    startMonitoring(): void {
        console.log("📊 Запуск Real-Time Monitoring");
        
        this.isRunning = true;
        
        // Запуск периодического обновления метрик
        this.updateInterval = setInterval(() => {
            this.updateMetrics();
            this.checkAlerts();
            this.updateDashboards();
        }, 5000); // Обновление каждые 5 секунд

        console.log("✅ Real-Time Monitoring запущен");
    }

    stopMonitoring(): void {
        console.log("🛑 Остановка Real-Time Monitoring");
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }

        this.isRunning = false;
        console.log("✅ Real-Time Monitoring остановлен");
    }

    recordMetric(metric: MonitoringMetric): void {
        console.log("📈 Запись метрики:", metric.name, "=", metric.value);
        
        metric.timestamp = new Date();
        this.metrics.set(metric.id, metric);
        
        // Проверка алертов для этой метрики
        this.checkMetricAlerts(metric);
    }

    recordEvent(event: MonitoringEvent): void {
        console.log("📝 Запись события:", event.type, event.severity);
        
        event.timestamp = new Date();
        this.events.push(event);
        
        // Ограничение истории событий (последние 1000)
        if (this.events.length > 1000) {
            this.events = this.events.slice(-1000);
        }
    }

    private updateMetrics(): void {
        // Обновление системных метрик
        this.recordMetric({
            id: "system-uptime",
            name: "System Uptime",
            type: "gauge",
            value: process.uptime(),
            labels: { component: "monitoring" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "memory-usage",
            name: "Memory Usage",
            type: "gauge",
            value: process.memoryUsage().heapUsed / 1024 / 1024, // MB
            labels: { component: "monitoring" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "active-events",
            name: "Active Events",
            type: "gauge",
            value: this.events.length,
            labels: { component: "monitoring" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "active-alerts",
            name: "Active Alerts",
            type: "gauge",
            value: Array.from(this.alerts.values()).filter(a => a.enabled).length,
            labels: { component: "monitoring" },
            timestamp: new Date()
        });
    }

    private checkAlerts(): void {
        for (const alert of this.alerts.values()) {
            if (!alert.enabled) continue;

            const metric = this.metrics.get(alert.condition.metricId);
            if (!metric) continue;

            if (this.evaluateAlertCondition(alert.condition, metric)) {
                this.triggerAlert(alert, metric);
            }
        }
    }

    private checkMetricAlerts(metric: MonitoringMetric): void {
        for (const alert of this.alerts.values()) {
            if (!alert.enabled || alert.condition.metricId !== metric.id) continue;

            if (this.evaluateAlertCondition(alert.condition, metric)) {
                this.triggerAlert(alert, metric);
            }
        }
    }

    private evaluateAlertCondition(condition: AlertCondition, metric: MonitoringMetric): boolean {
        switch (condition.operator) {
            case "greater":
                return metric.value > condition.threshold;
            case "less":
                return metric.value < condition.threshold;
            case "equals":
                return metric.value === condition.threshold;
            case "not_equals":
                return metric.value !== condition.threshold;
            default:
                return false;
        }
    }

    private triggerAlert(alert: MonitoringAlert, metric: MonitoringMetric): void {
        console.log("🚨 Сработал алерт:", alert.name, "для метрики:", metric.name);
        
        alert.lastTriggered = new Date();
        
        this.recordEvent({
            id: `alert-${Date.now()}`,
            type: "validation-failed",
            data: {
                alertId: alert.id,
                alertName: alert.name,
                metricId: metric.id,
                metricValue: metric.value,
                threshold: alert.condition.threshold,
                severity: alert.severity
            },
            timestamp: new Date(),
            severity: alert.severity === "critical" ? "critical" : "warning"
        });
    }

    private updateDashboards(): void {
        for (const dashboard of this.dashboards.values()) {
            this.updateDashboard(dashboard);
        }
    }

    private updateDashboard(dashboard: MonitoringDashboard): void {
        dashboard.lastUpdated = new Date();
        
        for (const widget of dashboard.widgets) {
            this.updateWidget(widget);
        }
    }

    private updateWidget(widget: DashboardWidget): void {
        switch (widget.type) {
            case "metric":
                widget.data = this.getMetricData(widget.id);
                break;
            case "chart":
                widget.data = this.getChartData(widget.id);
                break;
            case "alert":
                widget.data = this.getAlertData(widget.id);
                break;
            case "log":
                widget.data = this.getLogData(widget.id);
                break;
        }
    }

    private getMetricData(widgetId: string): any {
        // Возврат данных для метрики
        return {
            value: Math.random() * 100,
            trend: Math.random() > 0.5 ? "up" : "down",
            timestamp: new Date()
        };
    }

    private getChartData(widgetId: string): any {
        // Возврат данных для графика
        return {
            series: [
                { name: "Documents Generated", data: [10, 15, 12, 18, 20] },
                { name: "Diagrams Updated", data: [5, 8, 6, 10, 12] }
            ],
            categories: ["10:00", "10:05", "10:10", "10:15", "10:20"]
        };
    }

    private getAlertData(widgetId: string): any {
        // Возврат данных для алертов
        return {
            activeAlerts: Array.from(this.alerts.values()).filter(a => a.enabled).length,
            criticalAlerts: Array.from(this.alerts.values()).filter(a => a.severity === "critical").length,
            lastAlert: this.events.filter(e => e.type === "validation-failed").pop()
        };
    }

    private getLogData(widgetId: string): any {
        // Возврат данных для логов
        return {
            recentEvents: this.events.slice(-10),
            totalEvents: this.events.length
        };
    }

    private initializeDefaultMetrics(): void {
        console.log("🚀 Инициализация стандартных метрик");

        // Системные метрики
        this.recordMetric({
            id: "documents-generated",
            name: "Documents Generated",
            type: "counter",
            value: 0,
            labels: { component: "documentation" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "diagrams-updated",
            name: "Diagrams Updated",
            type: "counter",
            value: 0,
            labels: { component: "diagrams" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "validations-performed",
            name: "Validations Performed",
            type: "counter",
            value: 0,
            labels: { component: "validation" },
            timestamp: new Date()
        });

        this.recordMetric({
            id: "hooks-executed",
            name: "Hooks Executed",
            type: "counter",
            value: 0,
            labels: { component: "hooks" },
            timestamp: new Date()
        });

        console.log("✅ Стандартные метрики инициализированы");
    }

    private initializeDefaultAlerts(): void {
        console.log("🚀 Инициализация стандартных алертов");

        this.alerts.set("high-memory-usage", {
            id: "high-memory-usage",
            name: "High Memory Usage",
            condition: {
                metricId: "memory-usage",
                operator: "greater",
                threshold: 500, // 500 MB
                duration: 30000 // 30 секунд
            },
            severity: "high",
            message: "Использование памяти превышает 500 MB",
            enabled: true
        });

        this.alerts.set("validation-failures", {
            id: "validation-failures",
            name: "Validation Failures",
            condition: {
                metricId: "validations-performed",
                operator: "greater",
                threshold: 10,
                duration: 60000 // 1 минута
            },
            severity: "medium",
            message: "Количество валидаций превышает 10 в минуту",
            enabled: true
        });

        console.log("✅ Стандартные алерты инициализированы");
    }

    private initializeDefaultDashboards(): void {
        console.log("🚀 Инициализация стандартных дашбордов");

        this.dashboards.set("overview", {
            id: "overview",
            name: "Overview Dashboard",
            widgets: [
                {
                    id: "documents-metric",
                    type: "metric",
                    title: "Documents Generated",
                    data: {},
                    position: { x: 0, y: 0, width: 3, height: 2 }
                },
                {
                    id: "diagrams-chart",
                    type: "chart",
                    title: "Diagrams Activity",
                    data: {},
                    position: { x: 3, y: 0, width: 6, height: 4 }
                },
                {
                    id: "alerts-widget",
                    type: "alert",
                    title: "Active Alerts",
                    data: {},
                    position: { x: 9, y: 0, width: 3, height: 2 }
                },
                {
                    id: "events-log",
                    type: "log",
                    title: "Recent Events",
                    data: {},
                    position: { x: 0, y: 2, width: 12, height: 4 }
                }
            ],
            refreshInterval: 5000,
            lastUpdated: new Date()
        });

        console.log("✅ Стандартные дашборды инициализированы");
    }

    getMonitoringStatistics(): any {
        const totalMetrics = this.metrics.size;
        const totalAlerts = this.alerts.size;
        const enabledAlerts = Array.from(this.alerts.values()).filter(a => a.enabled).length;
        const totalEvents = this.events.length;
        const recentEvents = this.events.filter(e => 
            Date.now() - e.timestamp.getTime() < 3600000 // последний час
        ).length;

        const severityStats = {
            info: this.events.filter(e => e.severity === "info").length,
            warning: this.events.filter(e => e.severity === "warning").length,
            error: this.events.filter(e => e.severity === "error").length,
            critical: this.events.filter(e => e.severity === "critical").length
        };

        return {
            totalMetrics,
            totalAlerts,
            enabledAlerts,
            totalEvents,
            recentEvents,
            severityStats,
            isRunning: this.isRunning,
            uptime: process.uptime()
        };
    }

    getMetrics(): MonitoringMetric[] {
        return Array.from(this.metrics.values());
    }

    getAlerts(): MonitoringAlert[] {
        return Array.from(this.alerts.values());
    }

    getEvents(): MonitoringEvent[] {
        return [...this.events];
    }

    getDashboards(): MonitoringDashboard[] {
        return Array.from(this.dashboards.values());
    }
}
