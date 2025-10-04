import { ProjectInfo } from "../../types/ProjectTypes";
import { RFCDocument } from "../../types/RFCTypes";

export interface TeamRule {
    id: string;
    name: string;
    description: string;
    category: "coding-standards" | "documentation" | "architecture" | "security" | "process";
    scope: "global" | "project" | "file-type" | "component";
    conditions: RuleCondition[];
    actions: RuleAction[];
    enabled: boolean;
    priority: number;
    createdAt: Date;
    updatedAt: Date;
    author: string;
}

export interface RuleCondition {
    field: string;
    operator: "equals" | "contains" | "matches" | "exists" | "greater" | "less";
    value: any;
    description: string;
}

export interface RuleAction {
    type: "enforce" | "suggest" | "warn" | "block" | "auto-fix";
    message: string;
    parameters: any;
    severity: "low" | "medium" | "high" | "critical";
}

export interface RuleExecutionContext {
    project: ProjectInfo;
    filePath: string;
    content: string;
    user: string;
    mode: string;
    timestamp: Date;
}

export interface RuleExecutionResult {
    ruleId: string;
    ruleName: string;
    triggered: boolean;
    actions: RuleActionResult[];
    message: string;
    timestamp: Date;
}

export interface RuleActionResult {
    actionType: string;
    success: boolean;
    message: string;
    severity: string;
    data?: any;
}

export class TeamRulesIntegration {
    private rules: Map<string, TeamRule> = new Map();
    private executionHistory: RuleExecutionResult[] = [];

    constructor() {
        this.initializeDefaultRules();
    }

    registerRule(rule: TeamRule): void {
        console.log("📋 Регистрация Team Rule:", rule.name);
        rule.updatedAt = new Date();
        this.rules.set(rule.id, rule);
    }

    executeRules(context: RuleExecutionContext): Promise<RuleExecutionResult[]> {
        console.log("⚡ Выполнение Team Rules для файла:", context.filePath);
        
        const applicableRules = this.getApplicableRules(context);
        const results: Promise<RuleExecutionResult>[] = [];

        for (const rule of applicableRules) {
            results.push(this.executeRule(rule, context));
        }

        return Promise.all(results);
    }

    private getApplicableRules(context: RuleExecutionContext): TeamRule[] {
        const applicableRules: TeamRule[] = [];

        for (const rule of this.rules.values()) {
            if (!rule.enabled) continue;

            if (this.evaluateRuleConditions(rule, context)) {
                applicableRules.push(rule);
            }
        }

        // Сортировка по приоритету
        return applicableRules.sort((a, b) => b.priority - a.priority);
    }

    private evaluateRuleConditions(rule: TeamRule, context: RuleExecutionContext): boolean {
        for (const condition of rule.conditions) {
            if (!this.evaluateCondition(condition, context)) {
                return false;
            }
        }
        return true;
    }

    private evaluateCondition(condition: RuleCondition, context: RuleExecutionContext): boolean {
        const fieldValue = this.getFieldValue(context, condition.field);
        
        switch (condition.operator) {
            case "equals":
                return fieldValue === condition.value;
            case "contains":
                return String(fieldValue).includes(String(condition.value));
            case "matches":
                return new RegExp(condition.value).test(String(fieldValue));
            case "exists":
                return fieldValue !== undefined && fieldValue !== null && fieldValue !== "";
            case "greater":
                return Number(fieldValue) > Number(condition.value);
            case "less":
                return Number(fieldValue) < Number(condition.value);
            default:
                return false;
        }
    }

    private getFieldValue(context: RuleExecutionContext, field: string): any {
        const fieldMap: { [key: string]: any } = {
            "file-path": context.filePath,
            "file-extension": context.filePath.split('.').pop(),
            "content": context.content,
            "content-length": context.content.length,
            "project-type": context.project.type,
            "project-name": context.project.name,
            "user": context.user,
            "mode": context.mode,
            "timestamp": context.timestamp
        };
        return fieldMap[field];
    }

    private async executeRule(rule: TeamRule, context: RuleExecutionContext): Promise<RuleExecutionResult> {
        console.log("🔧 Выполнение Team Rule:", rule.name);
        
        const actions: RuleActionResult[] = [];
        let triggered = true;

        try {
            for (const action of rule.actions) {
                const actionResult = await this.executeAction(action, context);
                actions.push(actionResult);
                
                // Если действие блокирующее и не успешно, правило считается не сработавшим
                if (action.type === "block" && !actionResult.success) {
                    triggered = false;
                    break;
                }
            }

            const result: RuleExecutionResult = {
                ruleId: rule.id,
                ruleName: rule.name,
                triggered: triggered,
                actions: actions,
                message: triggered ? `Rule ${rule.name} executed successfully` : `Rule ${rule.name} blocked execution`,
                timestamp: new Date()
            };

            this.executionHistory.push(result);
            console.log("✅ Team Rule выполнен:", rule.name);

            return result;

        } catch (error) {
            const result: RuleExecutionResult = {
                ruleId: rule.id,
                ruleName: rule.name,
                triggered: false,
                actions: [{
                    actionType: "error",
                    success: false,
                    message: `Rule execution failed: ${error}`,
                    severity: "critical"
                }],
                message: `Rule ${rule.name} execution failed`,
                timestamp: new Date()
            };

            this.executionHistory.push(result);
            console.error("❌ Team Rule завершился с ошибкой:", rule.name, error);

            return result;
        }
    }

    private async executeAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        switch (action.type) {
            case "enforce":
                return this.executeEnforceAction(action, context);
            case "suggest":
                return this.executeSuggestAction(action, context);
            case "warn":
                return this.executeWarnAction(action, context);
            case "block":
                return this.executeBlockAction(action, context);
            case "auto-fix":
                return this.executeAutoFixAction(action, context);
            default:
                return {
                    actionType: action.type,
                    success: false,
                    message: `Unknown action type: ${action.type}`,
                    severity: "medium"
                };
        }
    }

    private async executeEnforceAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        console.log("🔒 Применение правила:", action.message);
        
        return {
            actionType: "enforce",
            success: true,
            message: action.message,
            severity: action.severity,
            data: { enforced: true, timestamp: new Date() }
        };
    }

    private async executeSuggestAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        console.log("💡 Предложение:", action.message);
        
        return {
            actionType: "suggest",
            success: true,
            message: action.message,
            severity: action.severity,
            data: { suggested: true, timestamp: new Date() }
        };
    }

    private async executeWarnAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        console.log("⚠️ Предупреждение:", action.message);
        
        return {
            actionType: "warn",
            success: true,
            message: action.message,
            severity: action.severity,
            data: { warning: true, timestamp: new Date() }
        };
    }

    private async executeBlockAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        console.log("🚫 Блокировка:", action.message);
        
        return {
            actionType: "block",
            success: true,
            message: action.message,
            severity: action.severity,
            data: { blocked: true, timestamp: new Date() }
        };
    }

    private async executeAutoFixAction(action: RuleAction, context: RuleExecutionContext): Promise<RuleActionResult> {
        console.log("🔧 Автоматическое исправление:", action.message);
        
        // Здесь будет логика автоматического исправления
        return {
            actionType: "auto-fix",
            success: true,
            message: action.message,
            severity: action.severity,
            data: { autoFixed: true, timestamp: new Date() }
        };
    }

    private initializeDefaultRules(): void {
        console.log("🚀 Инициализация стандартных Team Rules");

        // Правило для TypeScript файлов
        this.registerRule({
            id: "typescript-coding-standards",
            name: "TypeScript Coding Standards",
            description: "Стандарты кодирования для TypeScript файлов",
            category: "coding-standards",
            scope: "file-type",
            conditions: [
                {
                    field: "file-extension",
                    operator: "equals",
                    value: "ts",
                    description: "Файл должен быть TypeScript"
                }
            ],
            actions: [
                {
                    type: "enforce",
                    message: "Используйте строгую типизацию TypeScript",
                    parameters: {},
                    severity: "high"
                },
                {
                    type: "suggest",
                    message: "Добавьте JSDoc комментарии для публичных методов",
                    parameters: {},
                    severity: "medium"
                }
            ],
            enabled: true,
            priority: 100,
            createdAt: new Date(),
            updatedAt: new Date(),
            author: "Memory Bank System"
        });

        // Правило для RFC документов
        this.registerRule({
            id: "rfc-documentation-standards",
            name: "RFC Documentation Standards",
            description: "Стандарты документации для RFC файлов",
            category: "documentation",
            scope: "file-type",
            conditions: [
                {
                    field: "file-path",
                    operator: "contains",
                    value: "rfc",
                    description: "Файл должен быть RFC документом"
                }
            ],
            actions: [
                {
                    type: "enforce",
                    message: "RFC документ должен содержать Abstract, Context, Decision, Consequences",
                    parameters: {},
                    severity: "critical"
                },
                {
                    type: "suggest",
                    message: "Добавьте диаграммы для визуализации архитектурных решений",
                    parameters: {},
                    severity: "medium"
                }
            ],
            enabled: true,
            priority: 90,
            createdAt: new Date(),
            updatedAt: new Date(),
            author: "Memory Bank System"
        });

        // Правило для архитектурных файлов
        this.registerRule({
            id: "architecture-consistency",
            name: "Architecture Consistency",
            description: "Проверка консистентности архитектурных решений",
            category: "architecture",
            scope: "component",
            conditions: [
                {
                    field: "file-path",
                    operator: "contains",
                    value: "architecture",
                    description: "Файл должен быть архитектурным"
                }
            ],
            actions: [
                {
                    type: "warn",
                    message: "Проверьте соответствие архитектурным принципам проекта",
                    parameters: {},
                    severity: "medium"
                },
                {
                    type: "suggest",
                    message: "Обновите C4 диаграммы при изменении архитектуры",
                    parameters: {},
                    severity: "low"
                }
            ],
            enabled: true,
            priority: 80,
            createdAt: new Date(),
            updatedAt: new Date(),
            author: "Memory Bank System"
        });

        // Правило для безопасности
        this.registerRule({
            id: "security-guidelines",
            name: "Security Guidelines",
            description: "Руководящие принципы безопасности",
            category: "security",
            scope: "global",
            conditions: [
                {
                    field: "content",
                    operator: "contains",
                    value: "password",
                    description: "Файл содержит упоминание паролей"
                }
            ],
            actions: [
                {
                    type: "warn",
                    message: "Убедитесь, что пароли не хранятся в открытом виде",
                    parameters: {},
                    severity: "high"
                },
                {
                    type: "suggest",
                    message: "Используйте переменные окружения для чувствительных данных",
                    parameters: {},
                    severity: "medium"
                }
            ],
            enabled: true,
            priority: 95,
            createdAt: new Date(),
            updatedAt: new Date(),
            author: "Memory Bank System"
        });

        // Правило для Memory Bank workflow
        this.registerRule({
            id: "memory-bank-workflow",
            name: "Memory Bank Workflow",
            description: "Правила для Memory Bank workflow",
            category: "process",
            scope: "project",
            conditions: [
                {
                    field: "project-name",
                    operator: "contains",
                    value: "memory-bank",
                    description: "Проект должен быть Memory Bank"
                }
            ],
            actions: [
                {
                    type: "enforce",
                    message: "Следуйте VAN → PLAN → CREATIVE → IMPLEMENT → REFLECT → ARCHIVE workflow",
                    parameters: {},
                    severity: "high"
                },
                {
                    type: "suggest",
                    message: "Обновите activeContext.md при смене режима",
                    parameters: {},
                    severity: "medium"
                }
            ],
            enabled: true,
            priority: 85,
            createdAt: new Date(),
            updatedAt: new Date(),
            author: "Memory Bank System"
        });

        console.log("✅ Стандартные Team Rules инициализированы");
    }

    getRuleStatistics(): any {
        const totalRules = this.rules.size;
        const enabledRules = Array.from(this.rules.values()).filter(r => r.enabled).length;
        const totalExecutions = this.executionHistory.length;
        const triggeredRules = this.executionHistory.filter(r => r.triggered).length;
        
        const categoryStats: { [key: string]: number } = {};
        for (const rule of this.rules.values()) {
            categoryStats[rule.category] = (categoryStats[rule.category] || 0) + 1;
        }

        return {
            totalRules,
            enabledRules,
            totalExecutions,
            triggeredRules,
            triggerRate: totalExecutions > 0 ? (triggeredRules / totalExecutions) * 100 : 0,
            categoryStats,
            lastExecution: this.executionHistory.length > 0 ? this.executionHistory[this.executionHistory.length - 1].timestamp : null
        };
    }

    getExecutionHistory(): RuleExecutionResult[] {
        return [...this.executionHistory];
    }
}
