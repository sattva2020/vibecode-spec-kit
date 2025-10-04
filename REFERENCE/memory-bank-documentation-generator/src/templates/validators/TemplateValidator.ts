import { TemplateDefinition, TemplateVariable } from "../engine/TemplateEngine";
import { RFCDocument } from "../../types/RFCTypes";

export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    score: number;
}

export interface ValidationError {
    type: "critical" | "warning" | "info";
    message: string;
    field?: string;
    suggestion?: string;
}

export interface ValidationWarning {
    message: string;
    field?: string;
    suggestion?: string;
}

export interface ValidationRule {
    id: string;
    name: string;
    description: string;
    validate: (template: TemplateDefinition, data: any) => ValidationError[];
}

export class TemplateValidator {
    private validationRules: ValidationRule[] = [];

    constructor() {
        this.initializeDefaultRules();
    }

    validateTemplate(template: TemplateDefinition, data: any): ValidationResult {
        console.log("🔍 Валидация шаблона:", template.metadata.name);
        
        const errors: ValidationError[] = [];
        const warnings: ValidationWarning[] = [];
        
        // Проверка переменных
        const variableErrors = this.validateVariables(template, data);
        errors.push(...variableErrors);
        
        // Проверка контента
        const contentErrors = this.validateContent(template, data);
        errors.push(...contentErrors);
        
        // Проверка правилами
        for (const rule of this.validationRules) {
            try {
                const ruleErrors = rule.validate(template, data);
                errors.push(...ruleErrors);
            } catch (error) {
                console.error("❌ Ошибка в правиле валидации:", rule.name, error);
            }
        }
        
        // Генерация предупреждений
        const generatedWarnings = this.generateWarnings(template, data, errors);
        warnings.push(...generatedWarnings);
        
        // Расчет оценки
        const score = this.calculateScore(errors, warnings);
        
        const result: ValidationResult = {
            isValid: errors.filter(e => e.type === "critical").length === 0,
            errors: errors,
            warnings: warnings,
            score: score
        };
        
        console.log("📊 Результат валидации:", {
            isValid: result.isValid,
            errors: errors.length,
            warnings: warnings.length,
            score: score
        });
        
        return result;
    }

    validateDocument(document: RFCDocument): ValidationResult {
        console.log("🔍 Валидация RFC документа:", document.title);
        
        const errors: ValidationError[] = [];
        const warnings: ValidationWarning[] = [];
        
        // Проверка структуры документа
        if (!document.title || document.title.trim().length === 0) {
            errors.push({
                type: "critical",
                message: "Заголовок документа не может быть пустым",
                field: "title"
            });
        }
        
        if (!document.abstract || document.abstract.trim().length === 0) {
            errors.push({
                type: "critical",
                message: "Аннотация документа не может быть пустой",
                field: "abstract"
            });
        }
        
        if (!document.sections || document.sections.length === 0) {
            errors.push({
                type: "critical",
                message: "Документ должен содержать хотя бы одну секцию",
                field: "sections"
            });
        }
        
        // Проверка секций
        for (let i = 0; i < document.sections.length; i++) {
            const section = document.sections[i];
            
            if (!section.title || section.title.trim().length === 0) {
                errors.push({
                    type: "critical",
                    message: `Секция ${i + 1} должна иметь заголовок`,
                    field: `sections[${i}].title`
                });
            }
            
            if (!section.content || section.content.trim().length === 0) {
                warnings.push({
                    message: `Секция "${section.title}" не содержит контента`,
                    field: `sections[${i}].content`,
                    suggestion: "Добавьте содержание в секцию"
                });
            }
            
            if (section.content && section.content.length > 5000) {
                warnings.push({
                    message: `Секция "${section.title}" слишком длинная (${section.content.length} символов)`,
                    field: `sections[${i}].content`,
                    suggestion: "Рассмотрите возможность разбиения на подсекции"
                });
            }
        }
        
        // Проверка ссылок
        if (document.references && document.references.length > 0) {
            for (let i = 0; i < document.references.length; i++) {
                const reference = document.references[i];
                if (!reference || reference.trim().length === 0) {
                    errors.push({
                        type: "warning",
                        message: `Ссылка ${i + 1} пуста`,
                        field: `references[${i}]`
                    });
                }
            }
        }
        
        const score = this.calculateScore(errors, warnings);
        
        return {
            isValid: errors.filter(e => e.type === "critical").length === 0,
            errors: errors,
            warnings: warnings,
            score: score
        };
    }

    private validateVariables(template: TemplateDefinition, data: any): ValidationError[] {
        const errors: ValidationError[] = [];
        
        for (const variable of template.variables) {
            if (variable.required && !data.hasOwnProperty(variable.name)) {
                errors.push({
                    type: "critical",
                    message: `Обязательная переменная "${variable.name}" отсутствует`,
                    field: variable.name,
                    suggestion: `Добавьте значение для переменной: ${variable.description}`
                });
            }
            
            if (data.hasOwnProperty(variable.name)) {
                const value = data[variable.name];
                const typeError = this.validateVariableType(variable, value);
                if (typeError) {
                    errors.push(typeError);
                }
            }
        }
        
        return errors;
    }

    private validateVariableType(variable: TemplateVariable, value: any): ValidationError | null {
        switch (variable.type) {
            case "string":
                if (typeof value !== "string") {
                    return {
                        type: "critical",
                        message: `Переменная "${variable.name}" должна быть строкой`,
                        field: variable.name
                    };
                }
                break;
                
            case "number":
                if (typeof value !== "number") {
                    return {
                        type: "critical",
                        message: `Переменная "${variable.name}" должна быть числом`,
                        field: variable.name
                    };
                }
                break;
                
            case "boolean":
                if (typeof value !== "boolean") {
                    return {
                        type: "critical",
                        message: `Переменная "${variable.name}" должна быть булевым значением`,
                        field: variable.name
                    };
                }
                break;
                
            case "array":
                if (!Array.isArray(value)) {
                    return {
                        type: "critical",
                        message: `Переменная "${variable.name}" должна быть массивом`,
                        field: variable.name
                    };
                }
                break;
                
            case "object":
                if (typeof value !== "object" || Array.isArray(value)) {
                    return {
                        type: "critical",
                        message: `Переменная "${variable.name}" должна быть объектом`,
                        field: variable.name
                    };
                }
                break;
        }
        
        return null;
    }

    private validateContent(template: TemplateDefinition, data: any): ValidationError[] {
        const errors: ValidationError[] = [];
        
        try {
            const Mustache = require("mustache");
            const renderedContent = Mustache.render(template.content, data);
            
            // Проверка обязательных секций
            for (const requiredSection of template.validation.requiredSections) {
                if (!renderedContent.includes(requiredSection)) {
                    errors.push({
                        type: "critical",
                        message: `Отсутствует обязательная секция: "${requiredSection}"`,
                        suggestion: "Добавьте секцию в шаблон"
                    });
                }
            }
            
            // Проверка длины контента
            if (renderedContent.length > template.validation.maxLength) {
                errors.push({
                    type: "warning",
                    message: `Контент слишком длинный (${renderedContent.length} символов)`,
                    suggestion: `Максимальная длина: ${template.validation.maxLength} символов`
                });
            }
            
        } catch (error) {
            errors.push({
                type: "critical",
                message: `Ошибка рендеринга шаблона: ${error}`,
                suggestion: "Проверьте синтаксис шаблона"
            });
        }
        
        return errors;
    }

    private generateWarnings(template: TemplateDefinition, data: any, errors: ValidationError[]): ValidationWarning[] {
        const warnings: ValidationWarning[] = [];
        
        // Проверка на неиспользуемые переменные
        const usedVariables = this.extractUsedVariables(template.content);
        const unusedVariables = template.variables.filter(v => !usedVariables.includes(v.name));
        
        for (const variable of unusedVariables) {
            warnings.push({
                message: `Переменная "${variable.name}" определена, но не используется в шаблоне`,
                field: variable.name,
                suggestion: "Удалите неиспользуемую переменную или добавьте её в шаблон"
            });
        }
        
        // Проверка на отсутствующие переменные в данных
        for (const variableName of usedVariables) {
            if (!template.variables.find(v => v.name === variableName) && !data.hasOwnProperty(variableName)) {
                warnings.push({
                    message: `Переменная "${variableName}" используется в шаблоне, но не определена`,
                    field: variableName,
                    suggestion: "Добавьте определение переменной или значение в данные"
                });
            }
        }
        
        return warnings;
    }

    private extractUsedVariables(content: string): string[] {
        const variableRegex = /\{\{([^}]+)\}\}/g;
        const variables: string[] = [];
        let match;
        
        while ((match = variableRegex.exec(content)) !== null) {
            const variableName = match[1].trim();
            if (!variables.includes(variableName)) {
                variables.push(variableName);
            }
        }
        
        return variables;
    }

    private calculateScore(errors: ValidationError[], warnings: ValidationWarning[]): number {
        const criticalErrors = errors.filter(e => e.type === "critical").length;
        const warningErrors = errors.filter(e => e.type === "warning").length;
        const infoErrors = errors.filter(e => e.type === "info").length;
        
        let score = 100;
        score -= criticalErrors * 20; // Критические ошибки сильно снижают оценку
        score -= warningErrors * 10;  // Предупреждения умеренно снижают оценку
        score -= infoErrors * 5;      // Информационные сообщения слегка снижают оценку
        score -= warnings.length * 2; // Предупреждения валидатора слегка снижают оценку
        
        return Math.max(0, Math.min(100, score));
    }

    private initializeDefaultRules(): void {
        console.log("🚀 Инициализация правил валидации");
        
        // Правило проверки качества заголовков
        this.validationRules.push({
            id: "title-quality",
            name: "Title Quality Check",
            description: "Проверка качества заголовков",
            validate: (template, data) => {
                const errors: ValidationError[] = [];
                
                if (data.title) {
                    if (data.title.length < 5) {
                        errors.push({
                            type: "warning",
                            message: "Заголовок слишком короткий",
                            field: "title",
                            suggestion: "Добавьте более описательный заголовок"
                        });
                    }
                    
                    if (data.title.length > 100) {
                        errors.push({
                            type: "warning",
                            message: "Заголовок слишком длинный",
                            field: "title",
                            suggestion: "Сократите заголовок до 100 символов"
                        });
                    }
                }
                
                return errors;
            }
        });
        
        // Правило проверки аннотации
        this.validationRules.push({
            id: "abstract-quality",
            name: "Abstract Quality Check",
            description: "Проверка качества аннотации",
            validate: (template, data) => {
                const errors: ValidationError[] = [];
                
                if (data.abstract) {
                    if (data.abstract.length < 50) {
                        errors.push({
                            type: "warning",
                            message: "Аннотация слишком короткая",
                            field: "abstract",
                            suggestion: "Добавьте более подробную аннотацию"
                        });
                    }
                    
                    if (data.abstract.length > 500) {
                        errors.push({
                            type: "warning",
                            message: "Аннотация слишком длинная",
                            field: "abstract",
                            suggestion: "Сократите аннотацию до 500 символов"
                        });
                    }
                }
                
                return errors;
            }
        });
        
        // Правило проверки даты
        this.validationRules.push({
            id: "date-validation",
            name: "Date Validation",
            description: "Проверка корректности даты",
            validate: (template, data) => {
                const errors: ValidationError[] = [];
                
                if (data.date) {
                    const date = new Date(data.date);
                    if (isNaN(date.getTime())) {
                        errors.push({
                            type: "critical",
                            message: "Некорректный формат даты",
                            field: "date",
                            suggestion: "Используйте формат YYYY-MM-DD"
                        });
                    }
                }
                
                return errors;
            }
        });
        
        console.log("✅ Правила валидации инициализированы");
    }
}
