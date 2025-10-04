import { ProjectInfo } from "../../types/ProjectTypes";
import { RFCDocument } from "../../types/RFCTypes";
import { TemplateEngine } from "./TemplateEngine";

export interface ContentGenerationContext {
    project: ProjectInfo;
    timestamp: Date;
    user: string;
    environment: string;
    dependencies: string[];
}

export interface ContentGenerationRule {
    id: string;
    name: string;
    condition: (context: ContentGenerationContext) => boolean;
    action: (context: ContentGenerationContext) => any;
    priority: number;
}

export interface GeneratedContent {
    templateId: string;
    content: RFCDocument;
    metadata: {
        generatedAt: Date;
        generatedBy: string;
        context: ContentGenerationContext;
        rules: string[];
    };
}

export class DynamicContentGenerator {
    private templateEngine: TemplateEngine;
    private generationRules: ContentGenerationRule[] = [];

    constructor(templateEngine: TemplateEngine) {
        this.templateEngine = templateEngine;
        this.initializeDefaultRules();
    }

    generateContent(context: ContentGenerationContext, templateId: string): GeneratedContent {
        console.log("🎨 Генерация динамического контента для шаблона:", templateId);
        
        const applicableRules = this.getApplicableRules(context);
        const generatedData = this.applyRules(context, applicableRules);
        
        console.log("📊 Применено правил:", applicableRules.length);
        
        const content = this.templateEngine.renderDocument(templateId, generatedData);
        
        return {
            templateId: templateId,
            content: content,
            metadata: {
                generatedAt: new Date(),
                generatedBy: context.user,
                context: context,
                rules: applicableRules.map(rule => rule.id)
            }
        };
    }

    generateAllContent(context: ContentGenerationContext): GeneratedContent[] {
        console.log("🚀 Генерация всего контента для проекта:", context.project.name);
        
        const templates = this.templateEngine.getAvailableTemplates();
        const results: GeneratedContent[] = [];
        
        for (const template of templates) {
            try {
                const content = this.generateContent(context, template.metadata.id);
                results.push(content);
                console.log("✅ Сгенерирован контент для:", template.metadata.name);
            } catch (error) {
                console.error("❌ Ошибка генерации для шаблона:", template.metadata.name, error);
            }
        }
        
        console.log("📈 Всего сгенерировано контента:", results.length);
        return results;
    }

    addGenerationRule(rule: ContentGenerationRule): void {
        this.generationRules.push(rule);
        this.generationRules.sort((a, b) => b.priority - a.priority);
        console.log("➕ Добавлено правило генерации:", rule.name);
    }

    private getApplicableRules(context: ContentGenerationContext): ContentGenerationRule[] {
        return this.generationRules.filter(rule => {
            try {
                return rule.condition(context);
            } catch (error) {
                console.error("❌ Ошибка в правиле:", rule.name, error);
                return false;
            }
        });
    }

    private applyRules(context: ContentGenerationContext, rules: ContentGenerationRule[]): any {
        const result: any = {
            title: this.generateTitle(context),
            abstract: this.generateAbstract(context),
            status: "draft",
            date: context.timestamp.toISOString().split('T')[0],
            authors: context.user,
            ...context.project
        };

        for (const rule of rules) {
            try {
                const ruleResult = rule.action(context);
                Object.assign(result, ruleResult);
                console.log("🔧 Применено правило:", rule.name);
            } catch (error) {
                console.error("❌ Ошибка применения правила:", rule.name, error);
            }
        }

        return result;
    }

    private generateTitle(context: ContentGenerationContext): string {
        const projectName = context.project.name;
        const timestamp = context.timestamp.toLocaleDateString();
        return `${projectName} - Architecture Documentation (${timestamp})`;
    }

    private generateAbstract(context: ContentGenerationContext): string {
        return `Автоматически сгенерированная документация для проекта ${context.project.name}. ` +
               `Проект использует технологии: ${context.project.type}. ` +
               `Сгенерировано: ${context.timestamp.toLocaleString()}.`;
    }

    private initializeDefaultRules(): void {
        console.log("🚀 Инициализация правил генерации контента");

        // Правило для TypeScript проектов
        this.addGenerationRule({
            id: "typescript-project",
            name: "TypeScript Project Detection",
            condition: (context) => context.project.type === "nodejs" && 
                        context.project.dependencies.some(dep => dep.includes("typescript")),
            action: (context) => ({
                technologies: ["TypeScript", "Node.js"],
                language: "TypeScript",
                buildSystem: "npm/yarn",
                frameworks: context.project.dependencies.filter(dep => 
                    ["react", "vue", "angular", "express", "nestjs"].some(fw => dep.includes(fw))
                )
            }),
            priority: 100
        });

        // Правило для Rust проектов
        this.addGenerationRule({
            id: "rust-project",
            name: "Rust Project Detection",
            condition: (context) => context.project.type === "rust",
            action: (context) => ({
                technologies: ["Rust", "Cargo"],
                language: "Rust",
                buildSystem: "Cargo",
                frameworks: context.project.dependencies.filter(dep => 
                    ["tokio", "axum", "serde", "sqlx"].some(fw => dep.includes(fw))
                )
            }),
            priority: 100
        });

        // Правило для Python проектов
        this.addGenerationRule({
            id: "python-project",
            name: "Python Project Detection",
            condition: (context) => context.project.type === "python",
            action: (context) => ({
                technologies: ["Python"],
                language: "Python",
                buildSystem: "pip/poetry",
                frameworks: context.project.dependencies.filter(dep => 
                    ["fastapi", "django", "flask", "pandas", "numpy"].some(fw => dep.includes(fw))
                )
            }),
            priority: 100
        });

        // Правило для Memory Bank проектов
        this.addGenerationRule({
            id: "memory-bank-project",
            name: "Memory Bank Project Detection",
            condition: (context) => context.project.name.toLowerCase().includes("memory-bank") ||
                        context.project.path.includes("memory-bank"),
            action: (context) => ({
                projectType: "Memory Bank System",
                workflow: "VAN → PLAN → CREATIVE → IMPLEMENT → REFLECT → ARCHIVE",
                features: ["Task Management", "Creative Phase", "Implementation Tracking", "Reflection System"],
                architecture: "Event-Driven Architecture"
            }),
            priority: 200
        });

        // Правило для микросервисной архитектуры
        this.addGenerationRule({
            id: "microservices-architecture",
            name: "Microservices Architecture Detection",
            condition: (context) => context.project.dependencies.some(dep => 
                dep.includes("docker") || dep.includes("kubernetes") || dep.includes("microservice")
            ),
            action: (context) => ({
                architecture: "Microservices",
                deployment: "Containerized",
                orchestration: context.project.dependencies.some(dep => dep.includes("kubernetes")) ? "Kubernetes" : "Docker",
                communication: "REST/GraphQL APIs"
            }),
            priority: 80
        });

        // Правило для веб-приложений
        this.addGenerationRule({
            id: "web-application",
            name: "Web Application Detection",
            condition: (context) => context.project.dependencies.some(dep => 
                dep.includes("react") || dep.includes("vue") || dep.includes("angular") ||
                dep.includes("express") || dep.includes("fastapi") || dep.includes("django")
            ),
            action: (context) => ({
                applicationType: "Web Application",
                frontend: context.project.dependencies.filter(dep => 
                    ["react", "vue", "angular", "svelte"].some(fw => dep.includes(fw))
                )[0] || "Unknown",
                backend: context.project.dependencies.filter(dep => 
                    ["express", "fastapi", "django", "flask", "nestjs"].some(fw => dep.includes(fw))
                )[0] || "Unknown"
            }),
            priority: 70
        });

        console.log("✅ Правила генерации контента инициализированы");
    }
}
