import * as chokidar from "chokidar";
import { ProjectInfo } from "../../types/ProjectTypes";
import { RFCDocument } from "../../types/RFCTypes";

export interface UpdateTrigger {
    id: string;
    name: string;
    type: "file-change" | "time-based" | "manual" | "git-event";
    conditions: UpdateCondition[];
    actions: UpdateAction[];
    enabled: boolean;
    interval?: number; // для time-based триггеров
}

export interface UpdateCondition {
    field: string;
    operator: "equals" | "contains" | "matches" | "greater" | "less";
    value: any;
}

export interface UpdateAction {
    type: "regenerate-docs" | "update-diagrams" | "sync-git" | "notify" | "backup";
    parameters: any;
    priority: number;
}

export interface UpdateContext {
    project: ProjectInfo;
    changedFiles: string[];
    timestamp: Date;
    user: string;
    mode: string;
}

export interface UpdateResult {
    triggerId: string;
    success: boolean;
    message: string;
    actions: UpdateActionResult[];
    duration: number;
    timestamp: Date;
}

export interface UpdateActionResult {
    actionType: string;
    success: boolean;
    message: string;
    data?: any;
}

export class AutoUpdateSystem {
    private watcher: chokidar.FSWatcher | null = null;
    private triggers: Map<string, UpdateTrigger> = new Map();
    private updateHistory: UpdateResult[] = [];
    private isRunning: boolean = false;
    private projectPath: string = "";

    constructor() {
        this.initializeDefaultTriggers();
    }

    startWatching(projectPath: string): void {
        console.log("👁️ Запуск Auto-Update System для проекта:", projectPath);
        
        this.projectPath = projectPath;
        this.isRunning = true;

        // Настройка watcher для отслеживания изменений файлов
        this.watcher = chokidar.watch(projectPath, {
            ignored: /(^|[\/\\])\../, // игнорировать скрытые файлы
            persistent: true,
            ignoreInitial: true,
            depth: 10
        });

        this.watcher.on('change', (path) => this.handleFileChange(path));
        this.watcher.on('add', (path) => this.handleFileAdd(path));
        this.watcher.on('unlink', (path) => this.handleFileDelete(path));

        // Запуск time-based триггеров
        this.startTimeBasedTriggers();

        console.log("✅ Auto-Update System запущен");
    }

    stopWatching(): void {
        console.log("🛑 Остановка Auto-Update System");
        
        if (this.watcher) {
            this.watcher.close();
            this.watcher = null;
        }

        this.isRunning = false;
        console.log("✅ Auto-Update System остановлен");
    }

    private handleFileChange(path: string): void {
        console.log("📝 Файл изменен:", path);
        this.executeTriggers("file-change", { changedFiles: [path] });
    }

    private handleFileAdd(path: string): void {
        console.log("➕ Файл добавлен:", path);
        this.executeTriggers("file-change", { changedFiles: [path] });
    }

    private handleFileDelete(path: string): void {
        console.log("🗑️ Файл удален:", path);
        this.executeTriggers("file-change", { changedFiles: [path] });
    }

    private startTimeBasedTriggers(): void {
        for (const trigger of this.triggers.values()) {
            if (trigger.type === "time-based" && trigger.enabled && trigger.interval) {
                setInterval(() => {
                    this.executeTriggers("time-based", {});
                }, trigger.interval);
                
                console.log("⏰ Time-based триггер запущен:", trigger.name);
            }
        }
    }

    private async executeTriggers(type: string, context: any): Promise<void> {
        const applicableTriggers = this.getApplicableTriggers(type, context);
        
        for (const trigger of applicableTriggers) {
            await this.executeTrigger(trigger, context);
        }
    }

    private getApplicableTriggers(type: string, context: any): UpdateTrigger[] {
        const applicableTriggers: UpdateTrigger[] = [];

        for (const trigger of this.triggers.values()) {
            if (!trigger.enabled || trigger.type !== type) continue;

            if (this.evaluateTriggerConditions(trigger, context)) {
                applicableTriggers.push(trigger);
            }
        }

        // Сортировка по приоритету
        return applicableTriggers.sort((a, b) => {
            const aPriority = Math.max(...a.actions.map(action => action.priority));
            const bPriority = Math.max(...b.actions.map(action => action.priority));
            return bPriority - aPriority;
        });
    }

    private evaluateTriggerConditions(trigger: UpdateTrigger, context: any): boolean {
        for (const condition of trigger.conditions) {
            if (!this.evaluateCondition(condition, context)) {
                return false;
            }
        }
        return true;
    }

    private evaluateCondition(condition: UpdateCondition, context: any): boolean {
        const fieldValue = this.getFieldValue(context, condition.field);
        
        switch (condition.operator) {
            case "equals":
                return fieldValue === condition.value;
            case "contains":
                return String(fieldValue).includes(String(condition.value));
            case "matches":
                return new RegExp(condition.value).test(String(fieldValue));
            case "greater":
                return Number(fieldValue) > Number(condition.value);
            case "less":
                return Number(fieldValue) < Number(condition.value);
            default:
                return false;
        }
    }

    private getFieldValue(context: any, field: string): any {
        const fieldMap: { [key: string]: any } = {
            "file-path": context.changedFiles?.[0] || "",
            "file-extension": context.changedFiles?.[0]?.split('.').pop() || "",
            "timestamp": context.timestamp || new Date(),
            "user": context.user || "system"
        };
        return fieldMap[field];
    }

    private async executeTrigger(trigger: UpdateTrigger, context: any): Promise<void> {
        const startTime = Date.now();
        
        try {
            console.log("🔄 Выполнение Auto-Update триггера:", trigger.name);
            
            const actions: UpdateActionResult[] = [];
            
            for (const action of trigger.actions) {
                const actionResult = await this.executeAction(action, context);
                actions.push(actionResult);
            }

            const result: UpdateResult = {
                triggerId: trigger.id,
                success: actions.every(a => a.success),
                message: `Trigger ${trigger.name} executed successfully`,
                actions: actions,
                duration: Date.now() - startTime,
                timestamp: new Date()
            };

            this.updateHistory.push(result);
            console.log("✅ Auto-Update триггер выполнен:", trigger.name, `(${result.duration}ms)`);

        } catch (error) {
            const result: UpdateResult = {
                triggerId: trigger.id,
                success: false,
                message: `Trigger ${trigger.name} execution failed: ${error}`,
                actions: [{
                    actionType: "error",
                    success: false,
                    message: String(error)
                }],
                duration: Date.now() - startTime,
                timestamp: new Date()
            };

            this.updateHistory.push(result);
            console.error("❌ Auto-Update триггер завершился с ошибкой:", trigger.name, error);
        }
    }

    private async executeAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        switch (action.type) {
            case "regenerate-docs":
                return this.executeRegenerateDocsAction(action, context);
            case "update-diagrams":
                return this.executeUpdateDiagramsAction(action, context);
            case "sync-git":
                return this.executeSyncGitAction(action, context);
            case "notify":
                return this.executeNotifyAction(action, context);
            case "backup":
                return this.executeBackupAction(action, context);
            default:
                return {
                    actionType: action.type,
                    success: false,
                    message: `Unknown action type: ${action.type}`
                };
        }
    }

    private async executeRegenerateDocsAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        console.log("📝 Регенерация документации");
        
        try {
            // Здесь будет интеграция с генератором документации
            await new Promise(resolve => setTimeout(resolve, 1000)); // Симуляция
            
            return {
                actionType: "regenerate-docs",
                success: true,
                message: "Документация успешно регенерирована",
                data: { 
                    documentsGenerated: 3,
                    timestamp: new Date()
                }
            };
        } catch (error) {
            return {
                actionType: "regenerate-docs",
                success: false,
                message: `Ошибка регенерации документации: ${error}`
            };
        }
    }

    private async executeUpdateDiagramsAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        console.log("🎨 Обновление диаграмм");
        
        try {
            // Здесь будет интеграция с генератором диаграмм
            await new Promise(resolve => setTimeout(resolve, 500)); // Симуляция
            
            return {
                actionType: "update-diagrams",
                success: true,
                message: "Диаграммы успешно обновлены",
                data: { 
                    diagramsUpdated: 2,
                    timestamp: new Date()
                }
            };
        } catch (error) {
            return {
                actionType: "update-diagrams",
                success: false,
                message: `Ошибка обновления диаграмм: ${error}`
            };
        }
    }

    private async executeSyncGitAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        console.log("🔄 Синхронизация с Git");
        
        try {
            // Здесь будет интеграция с Git
            await new Promise(resolve => setTimeout(resolve, 200)); // Симуляция
            
            return {
                actionType: "sync-git",
                success: true,
                message: "Синхронизация с Git завершена",
                data: { 
                    commitHash: "abc123",
                    timestamp: new Date()
                }
            };
        } catch (error) {
            return {
                actionType: "sync-git",
                success: false,
                message: `Ошибка синхронизации с Git: ${error}`
            };
        }
    }

    private async executeNotifyAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        console.log("🔔 Отправка уведомления");
        
        try {
            // Здесь будет интеграция с системой уведомлений
            await new Promise(resolve => setTimeout(resolve, 100)); // Симуляция
            
            return {
                actionType: "notify",
                success: true,
                message: "Уведомление отправлено",
                data: { 
                    notificationSent: true,
                    timestamp: new Date()
                }
            };
        } catch (error) {
            return {
                actionType: "notify",
                success: false,
                message: `Ошибка отправки уведомления: ${error}`
            };
        }
    }

    private async executeBackupAction(action: UpdateAction, context: any): Promise<UpdateActionResult> {
        console.log("💾 Создание резервной копии");
        
        try {
            // Здесь будет логика создания резервной копии
            await new Promise(resolve => setTimeout(resolve, 300)); // Симуляция
            
            return {
                actionType: "backup",
                success: true,
                message: "Резервная копия создана",
                data: { 
                    backupCreated: true,
                    timestamp: new Date()
                }
            };
        } catch (error) {
            return {
                actionType: "backup",
                success: false,
                message: `Ошибка создания резервной копии: ${error}`
            };
        }
    }

    private initializeDefaultTriggers(): void {
        console.log("🚀 Инициализация стандартных Auto-Update триггеров");

        // Триггер для TypeScript файлов
        this.registerTrigger({
            id: "typescript-file-change",
            name: "TypeScript File Change",
            type: "file-change",
            conditions: [
                {
                    field: "file-extension",
                    operator: "equals",
                    value: "ts"
                }
            ],
            actions: [
                {
                    type: "regenerate-docs",
                    parameters: { templates: ["api", "architecture"] },
                    priority: 80
                }
            ],
            enabled: true
        });

        // Триггер для RFC файлов
        this.registerTrigger({
            id: "rfc-file-change",
            name: "RFC File Change",
            type: "file-change",
            conditions: [
                {
                    field: "file-path",
                    operator: "contains",
                    value: "rfc"
                }
            ],
            actions: [
                {
                    type: "update-diagrams",
                    parameters: { includeRelated: true },
                    priority: 90
                },
                {
                    type: "backup",
                    parameters: { includeMetadata: true },
                    priority: 70
                }
            ],
            enabled: true
        });

        // Триггер для регулярного обновления
        this.registerTrigger({
            id: "periodic-update",
            name: "Periodic Update",
            type: "time-based",
            conditions: [],
            actions: [
                {
                    type: "regenerate-docs",
                    parameters: { forceUpdate: true },
                    priority: 60
                },
                {
                    type: "sync-git",
                    parameters: { autoCommit: false },
                    priority: 50
                }
            ],
            enabled: false, // По умолчанию отключен
            interval: 300000 // 5 минут
        });

        console.log("✅ Стандартные Auto-Update триггеры инициализированы");
    }

    registerTrigger(trigger: UpdateTrigger): void {
        console.log("🔄 Регистрация Auto-Update триггера:", trigger.name);
        this.triggers.set(trigger.id, trigger);
    }

    getUpdateStatistics(): any {
        const totalTriggers = this.triggers.size;
        const enabledTriggers = Array.from(this.triggers.values()).filter(t => t.enabled).length;
        const totalUpdates = this.updateHistory.length;
        const successfulUpdates = this.updateHistory.filter(u => u.success).length;
        const averageDuration = this.updateHistory.reduce((sum, u) => sum + u.duration, 0) / totalUpdates;

        return {
            totalTriggers,
            enabledTriggers,
            totalUpdates,
            successfulUpdates,
            successRate: totalUpdates > 0 ? (successfulUpdates / totalUpdates) * 100 : 0,
            averageDuration: Math.round(averageDuration),
            isRunning: this.isRunning,
            projectPath: this.projectPath
        };
    }

    getUpdateHistory(): UpdateResult[] {
        return [...this.updateHistory];
    }
}
