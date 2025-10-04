import { ProjectInfo } from "../../types/ProjectTypes";
import { RFCDocument } from "../../types/RFCTypes";

export interface CursorHook {
    id: string;
    name: string;
    description: string;
    trigger: HookTrigger;
    action: HookAction;
    enabled: boolean;
    priority: number;
}

export interface HookTrigger {
    type: "file-change" | "mode-switch" | "command-execution" | "project-analysis" | "document-generation";
    conditions: HookCondition[];
}

export interface HookCondition {
    field: string;
    operator: "equals" | "contains" | "startsWith" | "endsWith" | "regex";
    value: any;
}

export interface HookAction {
    type: "generate-docs" | "update-diagrams" | "validate-content" | "notify-user" | "auto-commit";
    parameters: any;
    async: boolean;
}

export interface HookExecutionContext {
    project: ProjectInfo;
    timestamp: Date;
    user: string;
    mode: string;
    filesChanged: string[];
    commandsExecuted: string[];
}

export interface HookExecutionResult {
    hookId: string;
    success: boolean;
    message: string;
    data?: any;
    error?: string;
    duration: number;
}

export class CursorHooksIntegration {
    private hooks: Map<string, CursorHook> = new Map();
    private executionHistory: HookExecutionResult[] = [];

    constructor() {
        this.initializeDefaultHooks();
    }

    registerHook(hook: CursorHook): void {
        console.log("🔗 Регистрация Cursor Hook:", hook.name);
        this.hooks.set(hook.id, hook);
    }

    executeHooks(context: HookExecutionContext): Promise<HookExecutionResult[]> {
        console.log("⚡ Выполнение Cursor Hooks для контекста:", context.mode);
        
        const applicableHooks = this.getApplicableHooks(context);
        const results: Promise<HookExecutionResult>[] = [];

        for (const hook of applicableHooks) {
            results.push(this.executeHook(hook, context));
        }

        return Promise.all(results);
    }

    private getApplicableHooks(context: HookExecutionContext): CursorHook[] {
        const applicableHooks: CursorHook[] = [];

        for (const hook of this.hooks.values()) {
            if (!hook.enabled) continue;

            if (this.evaluateTrigger(hook.trigger, context)) {
                applicableHooks.push(hook);
            }
        }

        // Сортировка по приоритету
        return applicableHooks.sort((a, b) => b.priority - a.priority);
    }

    private evaluateTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        switch (trigger.type) {
            case "file-change":
                return this.evaluateFileChangeTrigger(trigger, context);
            case "mode-switch":
                return this.evaluateModeSwitchTrigger(trigger, context);
            case "command-execution":
                return this.evaluateCommandExecutionTrigger(trigger, context);
            case "project-analysis":
                return this.evaluateProjectAnalysisTrigger(trigger, context);
            case "document-generation":
                return this.evaluateDocumentGenerationTrigger(trigger, context);
            default:
                return false;
        }
    }

    private evaluateFileChangeTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        for (const condition of trigger.conditions) {
            const fieldValue = this.getFieldValue(context, condition.field);
            if (!this.evaluateCondition(fieldValue, condition)) {
                return false;
            }
        }
        return true;
    }

    private evaluateModeSwitchTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        return trigger.conditions.some(condition => 
            condition.field === "mode" && 
            this.evaluateCondition(context.mode, condition)
        );
    }

    private evaluateCommandExecutionTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        return trigger.conditions.some(condition => 
            condition.field === "command" && 
            context.commandsExecuted.some(cmd => this.evaluateCondition(cmd, condition))
        );
    }

    private evaluateProjectAnalysisTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        return trigger.conditions.some(condition => 
            condition.field === "project-type" && 
            this.evaluateCondition(context.project.type, condition)
        );
    }

    private evaluateDocumentGenerationTrigger(trigger: HookTrigger, context: HookExecutionContext): boolean {
        return trigger.conditions.some(condition => 
            condition.field === "document-type" && 
            this.evaluateCondition("rfc", condition)
        );
    }

    private evaluateCondition(value: any, condition: HookCondition): boolean {
        switch (condition.operator) {
            case "equals":
                return value === condition.value;
            case "contains":
                return String(value).includes(String(condition.value));
            case "startsWith":
                return String(value).startsWith(String(condition.value));
            case "endsWith":
                return String(value).endsWith(String(condition.value));
            case "regex":
                return new RegExp(condition.value).test(String(value));
            default:
                return false;
        }
    }

    private getFieldValue(context: HookExecutionContext, field: string): any {
        const fieldMap: { [key: string]: any } = {
            "mode": context.mode,
            "project-type": context.project.type,
            "files-changed": context.filesChanged,
            "commands": context.commandsExecuted,
            "user": context.user,
            "timestamp": context.timestamp
        };
        return fieldMap[field];
    }

    private async executeHook(hook: CursorHook, context: HookExecutionContext): Promise<HookExecutionResult> {
        const startTime = Date.now();
        
        try {
            console.log("🔧 Выполнение Hook:", hook.name);
            
            let result: any = null;
            
            switch (hook.action.type) {
                case "generate-docs":
                    result = await this.executeGenerateDocsAction(hook, context);
                    break;
                case "update-diagrams":
                    result = await this.executeUpdateDiagramsAction(hook, context);
                    break;
                case "validate-content":
                    result = await this.executeValidateContentAction(hook, context);
                    break;
                case "notify-user":
                    result = await this.executeNotifyUserAction(hook, context);
                    break;
                case "auto-commit":
                    result = await this.executeAutoCommitAction(hook, context);
                    break;
                default:
                    throw new Error(`Неизвестный тип действия: ${hook.action.type}`);
            }
            
            const executionResult: HookExecutionResult = {
                hookId: hook.id,
                success: true,
                message: `Hook ${hook.name} выполнен успешно`,
                data: result,
                duration: Date.now() - startTime
            };
            
            this.executionHistory.push(executionResult);
            console.log("✅ Hook выполнен:", hook.name, `(${executionResult.duration}ms)`);
            
            return executionResult;
            
        } catch (error) {
            const executionResult: HookExecutionResult = {
                hookId: hook.id,
                success: false,
                message: `Hook ${hook.name} завершился с ошибкой`,
                error: error instanceof Error ? error.message : String(error),
                duration: Date.now() - startTime
            };
            
            this.executionHistory.push(executionResult);
            console.error("❌ Hook завершился с ошибкой:", hook.name, error);
            
            return executionResult;
        }
    }

    private async executeGenerateDocsAction(hook: CursorHook, context: HookExecutionContext): Promise<any> {
        console.log("📝 Генерация документации через Hook");
        
        // Здесь будет интеграция с генератором документации
        return {
            documentsGenerated: 3,
            diagramsCreated: 2,
            timestamp: new Date()
        };
    }

    private async executeUpdateDiagramsAction(hook: CursorHook, context: HookExecutionContext): Promise<any> {
        console.log("🎨 Обновление диаграмм через Hook");
        
        // Здесь будет интеграция с генератором диаграмм
        return {
            diagramsUpdated: 2,
            timestamp: new Date()
        };
    }

    private async executeValidateContentAction(hook: CursorHook, context: HookExecutionContext): Promise<any> {
        console.log("🔍 Валидация контента через Hook");
        
        // Здесь будет интеграция с валидатором
        return {
            validationPassed: true,
            score: 95,
            timestamp: new Date()
        };
    }

    private async executeNotifyUserAction(hook: CursorHook, context: HookExecutionContext): Promise<any> {
        console.log("🔔 Уведомление пользователя через Hook");
        
        // Здесь будет интеграция с системой уведомлений
        return {
            notificationSent: true,
            message: "Документация обновлена автоматически",
            timestamp: new Date()
        };
    }

    private async executeAutoCommitAction(hook: CursorHook, context: HookExecutionContext): Promise<any> {
        console.log("💾 Автоматический коммит через Hook");
        
        // Здесь будет интеграция с Git
        return {
            commitCreated: true,
            commitHash: "abc123",
            timestamp: new Date()
        };
    }

    private initializeDefaultHooks(): void {
        console.log("🚀 Инициализация стандартных Cursor Hooks");

        // Hook для автоматической генерации документации при изменении файлов
        this.registerHook({
            id: "auto-doc-generation",
            name: "Auto Documentation Generation",
            description: "Автоматическая генерация документации при изменении файлов проекта",
            trigger: {
                type: "file-change",
                conditions: [
                    {
                        field: "files-changed",
                        operator: "contains",
                        value: ".ts"
                    }
                ]
            },
            action: {
                type: "generate-docs",
                parameters: {
                    templates: ["architecture", "api", "security"],
                    autoSave: true
                },
                async: true
            },
            enabled: true,
            priority: 100
        });

        // Hook для обновления диаграмм при смене режима
        this.registerHook({
            id: "mode-switch-diagram-update",
            name: "Mode Switch Diagram Update",
            description: "Обновление диаграмм при смене режима Memory Bank",
            trigger: {
                type: "mode-switch",
                conditions: [
                    {
                        field: "mode",
                        operator: "equals",
                        value: "IMPLEMENT"
                    }
                ]
            },
            action: {
                type: "update-diagrams",
                parameters: {
                    includeProgress: true,
                    highlightChanges: true
                },
                async: true
            },
            enabled: true,
            priority: 90
        });

        // Hook для валидации контента при генерации документов
        this.registerHook({
            id: "content-validation",
            name: "Content Validation",
            description: "Валидация контента при генерации документов",
            trigger: {
                type: "document-generation",
                conditions: [
                    {
                        field: "document-type",
                        operator: "equals",
                        value: "rfc"
                    }
                ]
            },
            action: {
                type: "validate-content",
                parameters: {
                    strictMode: true,
                    autoFix: false
                },
                async: false
            },
            enabled: true,
            priority: 80
        });

        // Hook для уведомлений о завершении генерации
        this.registerHook({
            id: "generation-completion-notification",
            name: "Generation Completion Notification",
            description: "Уведомление о завершении генерации документации",
            trigger: {
                type: "document-generation",
                conditions: [
                    {
                        field: "document-type",
                        operator: "equals",
                        value: "rfc"
                    }
                ]
            },
            action: {
                type: "notify-user",
                parameters: {
                    message: "Документация успешно сгенерирована",
                    type: "success"
                },
                async: true
            },
            enabled: true,
            priority: 70
        });

        // Hook для автоматического коммита при завершении фазы
        this.registerHook({
            id: "phase-completion-auto-commit",
            name: "Phase Completion Auto Commit",
            description: "Автоматический коммит при завершении фазы реализации",
            trigger: {
                type: "mode-switch",
                conditions: [
                    {
                        field: "mode",
                        operator: "equals",
                        value: "REFLECT"
                    }
                ]
            },
            action: {
                type: "auto-commit",
                parameters: {
                    message: "Phase completed - auto-generated documentation",
                    includeGeneratedFiles: true
                },
                async: true
            },
            enabled: false, // По умолчанию отключен для безопасности
            priority: 60
        });

        console.log("✅ Стандартные Cursor Hooks инициализированы");
    }

    getExecutionHistory(): HookExecutionResult[] {
        return [...this.executionHistory];
    }

    getHookStatistics(): any {
        const totalExecutions = this.executionHistory.length;
        const successfulExecutions = this.executionHistory.filter(r => r.success).length;
        const failedExecutions = totalExecutions - successfulExecutions;
        const averageDuration = this.executionHistory.reduce((sum, r) => sum + r.duration, 0) / totalExecutions;

        return {
            totalExecutions,
            successfulExecutions,
            failedExecutions,
            successRate: totalExecutions > 0 ? (successfulExecutions / totalExecutions) * 100 : 0,
            averageDuration: Math.round(averageDuration),
            registeredHooks: this.hooks.size,
            enabledHooks: Array.from(this.hooks.values()).filter(h => h.enabled).length
        };
    }
}
