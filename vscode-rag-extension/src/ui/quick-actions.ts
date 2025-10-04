import * as vscode from 'vscode';
import { RAGService } from '../services/rag-service';

export class QuickActions {
    private ragService: RAGService;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.ragService = new RAGService();
    }

    public registerCommands(): void {
        // Команда для быстрого анализа выделенного кода
        const analyzeSelectionCommand = vscode.commands.registerCommand(
            'rag-extension.analyzeSelection',
            async () => {
                await this.analyzeSelection();
            }
        );

        // Команда для генерации кода на основе комментария
        const generateFromCommentCommand = vscode.commands.registerCommand(
            'rag-extension.generateFromComment',
            async () => {
                await this.generateFromComment();
            }
        );

        // Команда для оптимизации выделенного кода
        const optimizeSelectionCommand = vscode.commands.registerCommand(
            'rag-extension.optimizeSelection',
            async () => {
                await this.optimizeSelection();
            }
        );

        // Команда для добавления документации к функции
        const addDocumentationCommand = vscode.commands.registerCommand(
            'rag-extension.addDocumentation',
            async () => {
                await this.addDocumentation();
            }
        );

        // Команда для исправления ошибок
        const fixErrorsCommand = vscode.commands.registerCommand(
            'rag-extension.fixErrors',
            async () => {
                await this.fixErrors();
            }
        );

        // Команда для рефакторинга кода
        const refactorCodeCommand = vscode.commands.registerCommand(
            'rag-extension.refactorCode',
            async () => {
                await this.refactorCode();
            }
        );

        // Команда для создания тестов
        const generateTestsCommand = vscode.commands.registerCommand(
            'rag-extension.generateTests',
            async () => {
                await this.generateTests();
            }
        );

        // Команды для показа предложений
        const showFunctionSuggestionsCommand = vscode.commands.registerCommand(
            'rag-extension.showFunctionSuggestions',
            async (func, suggestions) => {
                await this.showFunctionSuggestions(func, suggestions);
            }
        );

        const showClassImprovementsCommand = vscode.commands.registerCommand(
            'rag-extension.showClassImprovements',
            async (cls, improvements) => {
                await this.showClassImprovements(cls, improvements);
            }
        );

        // Команда для принятия предложения
        const acceptSuggestionCommand = vscode.commands.registerCommand(
            'rag-extension.acceptSuggestion',
            async (suggestion) => {
                await this.acceptSuggestion(suggestion);
            }
        );

        this.context.subscriptions.push(
            analyzeSelectionCommand,
            generateFromCommentCommand,
            optimizeSelectionCommand,
            addDocumentationCommand,
            fixErrorsCommand,
            refactorCodeCommand,
            generateTestsCommand,
            showFunctionSuggestionsCommand,
            showClassImprovementsCommand,
            acceptSuggestionCommand
        );
    }

    private async analyzeSelection(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Please select some code to analyze');
            return;
        }

        const selectedText = editor.document.getText(selection);
        
        try {
            vscode.window.showInformationMessage('🤖 Analyzing code...');
            const analysis = await this.ragService.analyzeCode({
                code: selectedText,
                language: 'typescript',
                filePath: editor.document.uri.fsPath
            });
            
            // Показываем результаты в новом документе
            const doc = await vscode.workspace.openTextDocument({
                content: `# Code Analysis Results\n\n\`\`\`json\n${JSON.stringify(analysis, null, 2)}\n\`\`\``,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to analyze code: ${error}`);
        }
    }

    private async generateFromComment(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const position = editor.selection.active;
        const line = editor.document.lineAt(position.line);
        
        // Ищем комментарий с TODO, FIXME, или HACK
        const commentMatch = line.text.match(/\/\/(?:TODO|FIXME|HACK|GENERATE):\s*(.+)/i);
        
        if (!commentMatch) {
            vscode.window.showWarningMessage('Please place cursor on a line with a TODO, FIXME, HACK, or GENERATE comment');
            return;
        }

        const prompt = commentMatch[1];
        
        try {
            vscode.window.showInformationMessage('🤖 Generating code...');
            const generatedCode = await this.ragService.generateCode(prompt);
            
            // Вставляем код после текущей строки
            const insertPosition = new vscode.Position(position.line + 1, 0);
            await editor.edit(editBuilder => {
                editBuilder.insert(insertPosition, `\n${generatedCode}\n`);
            });
            
            vscode.window.showInformationMessage('✅ Code generated successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate code: ${error}`);
        }
    }

    private async optimizeSelection(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Please select some code to optimize');
            return;
        }

        const selectedText = editor.document.getText(selection);
        
        try {
            vscode.window.showInformationMessage('🤖 Optimizing code...');
            const optimizedCode = await this.ragService.optimizeCode({
                code: selectedText,
                language: 'typescript',
                filePath: editor.document.uri.fsPath
            });
            
            // Заменяем выделенный код оптимизированной версией
            await editor.edit(editBuilder => {
                editBuilder.replace(selection, optimizedCode);
            });
            
            vscode.window.showInformationMessage('✅ Code optimized successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to optimize code: ${error}`);
        }
    }

    private async addDocumentation(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const position = editor.selection.active;
        const line = editor.document.lineAt(position.line);
        
        // Ищем функцию или класс на текущей строке
        const functionMatch = line.text.match(/(?:function\s+(\w+)|(\w+)\s*:\s*(?:async\s+)?\w+\s*=|(\w+)\s*\(\s*[^)]*\)\s*\{)/);
        const classMatch = line.text.match(/(?:class\s+(\w+)|interface\s+(\w+)|type\s+(\w+)\s*=)/);
        
        const name = functionMatch?.[1] || functionMatch?.[2] || functionMatch?.[3] || 
                    classMatch?.[1] || classMatch?.[2] || classMatch?.[3];
        
        if (!name) {
            vscode.window.showWarningMessage('Please place cursor on a function or class declaration');
            return;
        }

        const codeContext = this.getCodeContext(editor.document, position.line);
        
        try {
            vscode.window.showInformationMessage('🤖 Generating documentation...');
            const documentation = await this.ragService.generateDocumentation(name, codeContext);
            
            // Вставляем документацию перед текущей строкой
            const insertPosition = new vscode.Position(position.line, 0);
            await editor.edit(editBuilder => {
                editBuilder.insert(insertPosition, `${documentation}\n`);
            });
            
            vscode.window.showInformationMessage('✅ Documentation added successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate documentation: ${error}`);
        }
    }

    private async fixErrors(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        // Получаем диагностики для текущего документа
        const diagnostics = vscode.languages.getDiagnostics(editor.document.uri);
        if (diagnostics.length === 0) {
            vscode.window.showInformationMessage('No errors found in the current document');
            return;
        }

        try {
            vscode.window.showInformationMessage('🤖 Fixing errors...');
            
            // Исправляем ошибки одну за другой
            for (const diagnostic of diagnostics) {
                const errorCode = editor.document.getText(diagnostic.range);
                const fixedCode = await this.ragService.fixCodeError(errorCode, diagnostic.message);
                
                await editor.edit(editBuilder => {
                    editBuilder.replace(diagnostic.range, fixedCode);
                });
            }
            
            vscode.window.showInformationMessage(`✅ Fixed ${diagnostics.length} error(s)!`);
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to fix errors: ${error}`);
        }
    }

    private async refactorCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Please select some code to refactor');
            return;
        }

        const selectedText = editor.document.getText(selection);
        
        try {
            vscode.window.showInformationMessage('🤖 Refactoring code...');
            const refactoredCode = await this.ragService.refactorCode(selectedText);
            
            // Заменяем выделенный код рефакторенной версией
            await editor.edit(editBuilder => {
                editBuilder.replace(selection, refactoredCode);
            });
            
            vscode.window.showInformationMessage('✅ Code refactored successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to refactor code: ${error}`);
        }
    }

    private async generateTests(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Please select some code to generate tests for');
            return;
        }

        const selectedText = editor.document.getText(selection);
        
        try {
            vscode.window.showInformationMessage('🤖 Generating tests...');
            const testCode = await this.ragService.generateTests(selectedText);
            
            // Создаем новый файл с тестами
            const testFileName = editor.document.fileName.replace(/\.(ts|js)$/, '.test.$1');
            const doc = await vscode.workspace.openTextDocument({
                content: testCode,
                language: editor.document.languageId
            });
            await vscode.window.showTextDocument(doc);
            
            vscode.window.showInformationMessage('✅ Tests generated successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate tests: ${error}`);
        }
    }

    private async showFunctionSuggestions(func: any, suggestions: any[]): Promise<void> {
        const items = suggestions.map((suggestion, index) => ({
            label: `💡 ${suggestion.title}`,
            description: suggestion.description,
            detail: suggestion.code,
            index
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `AI suggestions for function: ${func.name}`,
            matchOnDescription: true,
            matchOnDetail: true
        });

        if (selected) {
            const suggestion = suggestions[selected.index];
            await this.applySuggestion(suggestion);
        }
    }

    private async showClassImprovements(cls: any, improvements: any[]): Promise<void> {
        const items = improvements.map((improvement, index) => ({
            label: `🔧 ${improvement.title}`,
            description: improvement.description,
            detail: improvement.code,
            index
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `AI improvements for class: ${cls.name}`,
            matchOnDescription: true,
            matchOnDetail: true
        });

        if (selected) {
            const improvement = improvements[selected.index];
            await this.applySuggestion(improvement);
        }
    }

    private async acceptSuggestion(suggestion: any): Promise<void> {
        await this.applySuggestion(suggestion);
    }

    private async applySuggestion(suggestion: any): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        
        try {
            await editor.edit(editBuilder => {
                if (suggestion.range) {
                    editBuilder.replace(suggestion.range, suggestion.code);
                } else {
                    editBuilder.insert(selection.active, suggestion.code);
                }
            });
            
            vscode.window.showInformationMessage('✅ Suggestion applied successfully!');
            
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to apply suggestion: ${error}`);
        }
    }

    private getCodeContext(document: vscode.TextDocument, lineIndex: number): string {
        const startLine = Math.max(0, lineIndex - 5);
        const endLine = Math.min(document.lineCount - 1, lineIndex + 10);
        
        const contextLines = [];
        for (let i = startLine; i <= endLine; i++) {
            contextLines.push(document.lineAt(i).text);
        }
        
        return contextLines.join('\n');
    }
}
