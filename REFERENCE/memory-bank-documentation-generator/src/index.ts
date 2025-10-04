import { IntegrationOrchestrator } from "./core/IntegrationOrchestrator";
import { ProjectAnalyzer } from "./analyzers/ProjectAnalyzer";
import { C4DiagramGenerator } from "./generators/C4DiagramGenerator";
import { RFCDocumentGenerator } from "./generators/RFCDocumentGenerator";
import { ProgressiveDisclosureUI } from "./core/ProgressiveDisclosureUI";
import { TemplateEngine } from "./templates/engine/TemplateEngine";
import { DynamicContentGenerator } from "./templates/engine/DynamicContentGenerator";
import { TemplateValidator } from "./templates/validators/TemplateValidator";
import { CursorHooksIntegration } from "./integrations/cursor-hooks/CursorHooksIntegration";
import { TeamRulesIntegration } from "./integrations/team-rules/TeamRulesIntegration";
import { AutoUpdateSystem } from "./integrations/auto-update/AutoUpdateSystem";
import { RealTimeMonitoring } from "./integrations/real-time-monitoring/RealTimeMonitoring";

export class DocumentationGenerator {
    private orchestrator: IntegrationOrchestrator;
    private projectAnalyzer: ProjectAnalyzer;
    private c4Generator: C4DiagramGenerator;
    private rfcGenerator: RFCDocumentGenerator;
    private progressiveUI: ProgressiveDisclosureUI;
    private templateEngine: TemplateEngine;
    private contentGenerator: DynamicContentGenerator;
    private validator: TemplateValidator;
    private cursorHooks: CursorHooksIntegration;
    private teamRules: TeamRulesIntegration;
    private autoUpdate: AutoUpdateSystem;
    private monitoring: RealTimeMonitoring;

    constructor() {
        this.orchestrator = new IntegrationOrchestrator();
        this.projectAnalyzer = new ProjectAnalyzer();
        this.c4Generator = new C4DiagramGenerator();
        this.rfcGenerator = new RFCDocumentGenerator();
        this.progressiveUI = new ProgressiveDisclosureUI();
        this.templateEngine = new TemplateEngine();
        this.contentGenerator = new DynamicContentGenerator(this.templateEngine);
        this.validator = new TemplateValidator();
        this.cursorHooks = new CursorHooksIntegration();
        this.teamRules = new TeamRulesIntegration();
        this.autoUpdate = new AutoUpdateSystem();
        this.monitoring = new RealTimeMonitoring();
        
        // Инициализация шаблонов
        this.templateEngine.initializeDefaultTemplates();
        
        // Запуск мониторинга
        this.monitoring.startMonitoring();
    }

    async generateDocumentation(projectPath: string): Promise<void> {
        console.log("🚀 Начинаем генерацию документации для проекта:", projectPath);
        
        const projectInfo = await this.projectAnalyzer.analyzeProject(projectPath);
        console.log("📊 Проект проанализирован:", projectInfo.name);
        
        const c4Diagrams = await this.generateC4Diagrams(projectInfo);
        console.log("📈 C4 диаграммы сгенерированы:", c4Diagrams.length);
        
        const rfcDocuments = await this.generateRFCDocuments(projectInfo);
        console.log("📋 RFC документы созданы:", rfcDocuments.length);
        
        await this.initializeProgressiveUI(c4Diagrams);
        console.log("🎨 Progressive Disclosure UI инициализирован");
        
        await this.generateDynamicContent(projectInfo);
        console.log("🎯 Динамический контент сгенерирован");
        
        await this.executeCursorIntegrations(projectInfo);
        console.log("🔗 Cursor интеграции выполнены");
        
        await this.startAutoUpdateSystem(projectPath);
        console.log("🔄 Auto-Update система запущена");
        
        console.log("✅ Генерация документации завершена!");
    }

    private async generateC4Diagrams(project: any): Promise<any[]> {
        const diagrams = [];
        const systemContext = this.c4Generator.generateSystemContext(project);
        const containerDiagram = this.c4Generator.generateContainerDiagram(project);
        const componentDiagram = this.c4Generator.generateComponentDiagram(project);
        
        diagrams.push(systemContext);
        diagrams.push(containerDiagram);
        diagrams.push(componentDiagram);
        
        return diagrams;
    }

    private async generateRFCDocuments(project: any): Promise<any[]> {
        const documents = [];
        documents.push(this.rfcGenerator.buildArchitectureDecisions(project));
        documents.push(this.rfcGenerator.buildTechnicalStandards(project));
        documents.push(this.rfcGenerator.buildSecurityGuidelines(project));
        
        return documents;
    }

    private async initializeProgressiveUI(diagrams: any[]): Promise<void> {
        console.log("🎨 Инициализация Progressive Disclosure UI для", diagrams.length, "диаграмм");
        
        for (const diagram of diagrams) {
            this.progressiveUI.initializeDiagram(diagram);
            console.log("✅ Диаграмма", diagram.title, "инициализирована");
        }
        
        console.log("🎯 Демонстрация фильтрации:");
        this.progressiveUI.applyFilters({
            showContainers: true, 
            showComponents: false, 
            showRelationships: true, 
            showTechnologies: true, 
            complexityThreshold: { level: "medium", threshold: 25 }
        });
        
        console.log("🔍 Демонстрация zoom:");
        this.progressiveUI.zoomToElement("memory-bank-core");
        
        console.log("✨ Демонстрация подсветки:");
        this.progressiveUI.highlightElement("memory-bank-core");
    }

    private async generateDynamicContent(project: any): Promise<void> {
        console.log("🎨 Генерация динамического контента с шаблонами");
        
        const context = {
            project: project,
            timestamp: new Date(),
            user: "Memory Bank System",
            environment: "development",
            dependencies: project.dependencies
        };
        
        // Генерация контента для всех шаблонов
        const generatedContent = this.contentGenerator.generateAllContent(context);
        
        console.log("📊 Сгенерировано контента:", generatedContent.length);
        
        // Валидация и сохранение
        for (const content of generatedContent) {
            const validation = this.validator.validateDocument(content.content);
            
            console.log(`📋 Валидация ${content.templateId}:`, {
                isValid: validation.isValid,
                score: validation.score,
                errors: validation.errors.length,
                warnings: validation.warnings.length
            });
            
            if (validation.isValid) {
                await this.saveRFCDocument(content.content);
                console.log("✅ RFC документ сохранен:", content.content.title);
            } else {
                console.error("❌ RFC документ не прошел валидацию:", content.content.title);
            }
        }
    }

    private async saveRFCDocument(document: any): Promise<void> {
        const fs = require("fs");
        const path = require("path");
        
        const outputDir = path.join(__dirname, "../../docs/generated/rfc-documents");
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const fileName = `${document.id}.md`;
        const filePath = path.join(outputDir, fileName);
        
        const markdownContent = this.generateMarkdownFromRFC(document);
        fs.writeFileSync(filePath, markdownContent);
        
        console.log("💾 RFC документ сохранен:", filePath);
    }

    private generateMarkdownFromRFC(document: any): string {
        let markdown = `# ${document.title}\n\n`;
        markdown += `**Status:** ${document.status}\n`;
        markdown += `**Last Updated:** ${document.lastUpdated.toISOString()}\n\n`;
        markdown += `## Abstract\n\n${document.abstract}\n\n`;
        
        for (const section of document.sections) {
            markdown += `## ${section.title}\n\n${section.content}\n\n`;
        }
        
        if (document.references && document.references.length > 0) {
            markdown += `## References\n\n`;
            for (const ref of document.references) {
                markdown += `- ${ref}\n`;
            }
        }
        
        return markdown;
    }

    private async executeCursorIntegrations(projectInfo: any): Promise<void> {
        console.log("🔗 Выполнение Cursor интеграций");
        
        const context = {
            project: projectInfo,
            timestamp: new Date(),
            user: "Memory Bank System",
            mode: "IMPLEMENT",
            filesChanged: [],
            commandsExecuted: ["npm run build", "npm test"]
        };

        // Выполнение Cursor Hooks
        const hookResults = await this.cursorHooks.executeHooks(context);
        console.log("⚡ Cursor Hooks выполнены:", hookResults.length);

        // Выполнение Team Rules
        const ruleContext = {
            project: projectInfo,
            filePath: "src/index.ts",
            content: "export class DocumentationGenerator",
            user: "Memory Bank System",
            mode: "IMPLEMENT",
            timestamp: new Date()
        };
        
        const ruleResults = await this.teamRules.executeRules(ruleContext);
        console.log("📋 Team Rules выполнены:", ruleResults.length);

        // Запись метрик
        this.monitoring.recordMetric({
            id: "hooks-executed",
            name: "Hooks Executed",
            type: "counter",
            value: hookResults.length,
            labels: { component: "cursor-hooks" },
            timestamp: new Date()
        });

        this.monitoring.recordEvent({
            id: `integration-${Date.now()}`,
            type: "hook-executed",
            data: { hooksExecuted: hookResults.length, rulesExecuted: ruleResults.length },
            timestamp: new Date(),
            severity: "info"
        });
    }

    private async startAutoUpdateSystem(projectPath: string): Promise<void> {
        console.log("🔄 Запуск Auto-Update системы");
        
        this.autoUpdate.startWatching(projectPath);
        
        // Запись метрик
        this.monitoring.recordMetric({
            id: "auto-update-enabled",
            name: "Auto Update Enabled",
            type: "gauge",
            value: 1,
            labels: { component: "auto-update" },
            timestamp: new Date()
        });

        this.monitoring.recordEvent({
            id: `auto-update-${Date.now()}`,
            type: "document-generated",
            data: { projectPath: projectPath, autoUpdateEnabled: true },
            timestamp: new Date(),
            severity: "info"
        });
    }

    getSystemStatus(): any {
        const hookStats = this.cursorHooks.getHookStatistics();
        const ruleStats = this.teamRules.getRuleStatistics();
        const updateStats = this.autoUpdate.getUpdateStatistics();
        const monitoringStats = this.monitoring.getMonitoringStatistics();

        return {
            hooks: hookStats,
            rules: ruleStats,
            autoUpdate: updateStats,
            monitoring: monitoringStats,
            timestamp: new Date()
        };
    }
}

// Demo функция
async function demo() {
    const generator = new DocumentationGenerator();
    await generator.generateDocumentation("E:/My/vibecode-ide");
}

if (require.main === module) {
    demo().catch(console.error);
}