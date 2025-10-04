import * as Mustache from "mustache";
import { RFCDocument, RFCSection } from "../../types/RFCTypes";

export interface TemplateMetadata {
    id: string;
    name: string;
    version: string;
    description: string;
    category: "architecture" | "api" | "security" | "process" | "standard";
    tags: string[];
    author: string;
    lastModified: Date;
}

export interface TemplateVariable {
    name: string;
    type: "string" | "number" | "boolean" | "array" | "object";
    required: boolean;
    defaultValue?: any;
    description: string;
}

export interface TemplateDefinition {
    metadata: TemplateMetadata;
    variables: TemplateVariable[];
    content: string;
    validation: TemplateValidation;
}

export interface TemplateValidation {
    requiredSections: string[];
    maxLength: number;
    minSections: number;
    allowedFormats: string[];
}

export class TemplateEngine {
    private templates: Map<string, TemplateDefinition> = new Map();
    private compiledTemplates: Map<string, string> = new Map();

    registerTemplate(template: TemplateDefinition): void {
        console.log("📝 Регистрация шаблона:", template.metadata.name);
        this.templates.set(template.metadata.id, template);
        this.compileTemplate(template);
    }

    compileTemplate(template: TemplateDefinition): string {
        try {
            const compiled = Mustache.render(template.content, {});
            this.compiledTemplates.set(template.metadata.id, compiled);
            console.log("✅ Шаблон скомпилирован:", template.metadata.name);
            return compiled;
        } catch (error) {
            console.error("❌ Ошибка компиляции шаблона:", template.metadata.name, error);
            throw error;
        }
    }

    renderDocument(templateId: string, data: any): RFCDocument {
        const template = this.templates.get(templateId);
        if (!template) {
            throw new Error(`Шаблон не найден: ${templateId}`);
        }

        console.log("🎨 Рендеринг документа с шаблоном:", template.metadata.name);
        
        const renderedContent = Mustache.render(template.content, data);
        const sections = this.parseRenderedContent(renderedContent);
        
        return {
            id: data.id || `rfc-${Date.now()}`,
            title: data.title || template.metadata.name,
            abstract: data.abstract || template.metadata.description,
            status: data.status || "draft",
            sections: sections,
            references: data.references || [],
            lastUpdated: new Date()
        };
    }

    getAvailableTemplates(category?: string): TemplateDefinition[] {
        const templates = Array.from(this.templates.values());
        if (category) {
            return templates.filter(t => t.metadata.category === category);
        }
        return templates;
    }

    validateTemplate(templateId: string, data: any): boolean {
        const template = this.templates.get(templateId);
        if (!template) {
            return false;
        }

        console.log("🔍 Валидация шаблона:", template.metadata.name);
        
        // Проверка обязательных переменных
        for (const variable of template.variables) {
            if (variable.required && !data[variable.name]) {
                console.error("❌ Отсутствует обязательная переменная:", variable.name);
                return false;
            }
        }

        // Проверка валидации контента
        if (template.validation.requiredSections.length > 0) {
            const renderedContent = Mustache.render(template.content, data);
            for (const section of template.validation.requiredSections) {
                if (!renderedContent.includes(section)) {
                    console.error("❌ Отсутствует обязательная секция:", section);
                    return false;
                }
            }
        }

        console.log("✅ Валидация шаблона прошла успешно");
        return true;
    }

    private parseRenderedContent(content: string): RFCSection[] {
        const sections: RFCSection[] = [];
        const lines = content.split('\n');
        let currentSection: RFCSection | null = null;
        
        for (const line of lines) {
            if (line.startsWith('## ')) {
                if (currentSection) {
                    sections.push(currentSection);
                }
                currentSection = {
                    id: this.generateSectionId(line.substring(3)),
                    title: line.substring(3),
                    content: "",
                    type: "text"
                };
            } else if (currentSection) {
                currentSection.content += line + '\n';
            }
        }
        
        if (currentSection) {
            sections.push(currentSection);
        }
        
        return sections;
    }

    private generateSectionId(title: string): string {
        return title.toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, '-')
            .substring(0, 50);
    }

    initializeDefaultTemplates(): void {
        console.log("🚀 Инициализация стандартных шаблонов");
        
        // Архитектурные решения
        this.registerTemplate(this.createArchitectureTemplate());
        
        // API дизайн
        this.registerTemplate(this.createAPITemplate());
        
        // Безопасность
        this.registerTemplate(this.createSecurityTemplate());
        
        // Процессы
        this.registerTemplate(this.createProcessTemplate());
        
        // Стандарты
        this.registerTemplate(this.createStandardTemplate());
        
        console.log("✅ Стандартные шаблоны инициализированы");
    }

    private createArchitectureTemplate(): TemplateDefinition {
        return {
            metadata: {
                id: "architecture-decisions",
                name: "Architecture Decisions",
                version: "1.0.0",
                description: "Шаблон для документирования архитектурных решений",
                category: "architecture",
                tags: ["architecture", "decisions", "design"],
                author: "Memory Bank System",
                lastModified: new Date()
            },
            variables: [
                {
                    name: "title",
                    type: "string",
                    required: true,
                    description: "Название архитектурного решения"
                },
                {
                    name: "context",
                    type: "string",
                    required: true,
                    description: "Контекст решения"
                },
                {
                    name: "decision",
                    type: "string",
                    required: true,
                    description: "Принятое решение"
                },
                {
                    name: "consequences",
                    type: "array",
                    required: true,
                    description: "Последствия решения"
                }
            ],
            content: `# {{title}}

**Status:** {{status}}  
**Date:** {{date}}  
**Authors:** {{authors}}

## Abstract

{{abstract}}

## Context

{{context}}

## Decision

{{decision}}

## Consequences

{{#consequences}}
- {{.}}
{{/consequences}}

## References

{{#references}}
- {{.}}
{{/references}}`,
            validation: {
                requiredSections: ["Context", "Decision", "Consequences"],
                maxLength: 10000,
                minSections: 3,
                allowedFormats: ["markdown"]
            }
        };
    }

    private createAPITemplate(): TemplateDefinition {
        return {
            metadata: {
                id: "api-design",
                name: "API Design",
                version: "1.0.0",
                description: "Шаблон для документирования API дизайна",
                category: "api",
                tags: ["api", "design", "rest", "graphql"],
                author: "Memory Bank System",
                lastModified: new Date()
            },
            variables: [
                {
                    name: "title",
                    type: "string",
                    required: true,
                    description: "Название API"
                },
                {
                    name: "version",
                    type: "string",
                    required: true,
                    description: "Версия API"
                },
                {
                    name: "endpoints",
                    type: "array",
                    required: true,
                    description: "Список эндпоинтов"
                }
            ],
            content: `# {{title}} API Design

**Version:** {{version}}  
**Status:** {{status}}  
**Date:** {{date}}

## Abstract

{{abstract}}

## API Overview

{{overview}}

## Endpoints

{{#endpoints}}
### {{method}} {{path}}

**Description:** {{description}}

**Request Body:**
\`\`\`json
{{requestBody}}
\`\`\`

**Response:**
\`\`\`json
{{response}}
\`\`\`

---
{{/endpoints}}

## Authentication

{{authentication}}

## Error Handling

{{errorHandling}}

## Rate Limiting

{{rateLimiting}}`,
            validation: {
                requiredSections: ["API Overview", "Endpoints"],
                maxLength: 15000,
                minSections: 4,
                allowedFormats: ["markdown"]
            }
        };
    }

    private createSecurityTemplate(): TemplateDefinition {
        return {
            metadata: {
                id: "security-guidelines",
                name: "Security Guidelines",
                version: "1.0.0",
                description: "Шаблон для документирования руководящих принципов безопасности",
                category: "security",
                tags: ["security", "guidelines", "best-practices"],
                author: "Memory Bank System",
                lastModified: new Date()
            },
            variables: [
                {
                    name: "title",
                    type: "string",
                    required: true,
                    description: "Название документа безопасности"
                },
                {
                    name: "threats",
                    type: "array",
                    required: true,
                    description: "Список угроз"
                },
                {
                    name: "mitigations",
                    type: "array",
                    required: true,
                    description: "Способы снижения рисков"
                }
            ],
            content: `# {{title}}

**Status:** {{status}}  
**Date:** {{date}}  
**Security Level:** {{securityLevel}}

## Abstract

{{abstract}}

## Threat Model

{{threatModel}}

## Identified Threats

{{#threats}}
### {{title}}

**Severity:** {{severity}}  
**Description:** {{description}}  
**Impact:** {{impact}}

**Mitigation:**
{{mitigation}}

---
{{/threats}}

## Security Controls

{{#mitigations}}
- **{{name}}:** {{description}}
{{/mitigations}}

## Compliance

{{compliance}}

## Monitoring

{{monitoring}}

## Incident Response

{{incidentResponse}}`,
            validation: {
                requiredSections: ["Threat Model", "Security Controls"],
                maxLength: 12000,
                minSections: 4,
                allowedFormats: ["markdown"]
            }
        };
    }

    private createProcessTemplate(): TemplateDefinition {
        return {
            metadata: {
                id: "process-definition",
                name: "Process Definition",
                version: "1.0.0",
                description: "Шаблон для документирования процессов разработки",
                category: "process",
                tags: ["process", "workflow", "development"],
                author: "Memory Bank System",
                lastModified: new Date()
            },
            variables: [
                {
                    name: "title",
                    type: "string",
                    required: true,
                    description: "Название процесса"
                },
                {
                    name: "steps",
                    type: "array",
                    required: true,
                    description: "Шаги процесса"
                }
            ],
            content: `# {{title}}

**Status:** {{status}}  
**Date:** {{date}}  
**Owner:** {{owner}}

## Abstract

{{abstract}}

## Process Overview

{{overview}}

## Process Steps

{{#steps}}
### {{number}}. {{title}}

**Description:** {{description}}  
**Responsible:** {{responsible}}  
**Duration:** {{duration}}  
**Dependencies:** {{dependencies}}

**Actions:**
{{#actions}}
- {{.}}
{{/actions}}

**Deliverables:**
{{#deliverables}}
- {{.}}
{{/deliverables}}

---
{{/steps}}

## Roles and Responsibilities

{{roles}}

## Tools and Technologies

{{tools}}

## Metrics and KPIs

{{metrics}}

## Continuous Improvement

{{improvement}}`,
            validation: {
                requiredSections: ["Process Overview", "Process Steps"],
                maxLength: 8000,
                minSections: 3,
                allowedFormats: ["markdown"]
            }
        };
    }

    private createStandardTemplate(): TemplateDefinition {
        return {
            metadata: {
                id: "technical-standard",
                name: "Technical Standard",
                version: "1.0.0",
                description: "Шаблон для документирования технических стандартов",
                category: "standard",
                tags: ["standard", "technical", "guidelines"],
                author: "Memory Bank System",
                lastModified: new Date()
            },
            variables: [
                {
                    name: "title",
                    type: "string",
                    required: true,
                    description: "Название стандарта"
                },
                {
                    name: "rules",
                    type: "array",
                    required: true,
                    description: "Правила стандарта"
                }
            ],
            content: `# {{title}}

**Version:** {{version}}  
**Status:** {{status}}  
**Date:** {{date}}  
**Scope:** {{scope}}

## Abstract

{{abstract}}

## Purpose

{{purpose}}

## Scope and Applicability

{{scope}}

## Standards and Rules

{{#rules}}
### {{category}}

{{#items}}
- **{{name}}:** {{description}}
{{/items}}

---
{{/rules}}

## Implementation Guidelines

{{implementation}}

## Compliance

{{compliance}}

## Review Process

{{review}}

## References

{{#references}}
- {{.}}
{{/references}}`,
            validation: {
                requiredSections: ["Purpose", "Standards and Rules"],
                maxLength: 10000,
                minSections: 4,
                allowedFormats: ["markdown"]
            }
        };
    }
}
