import * as vscode from 'vscode';
import { RAGService } from '../services/rag-service';

export class AICodeLensProvider implements vscode.CodeLensProvider {
    private ragService: RAGService;
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

    constructor() {
        this.ragService = new RAGService();
    }

    refresh() {
        this._onDidChangeCodeLenses.fire();
    }

    async provideCodeLenses(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): Promise<vscode.CodeLens[] | null | undefined> {
        try {
            const codeLenses: vscode.CodeLens[] = [];
            
            // Анализируем код для поиска функций и классов
            const functions = this.extractFunctions(document);
            const classes = this.extractClasses(document);
            
            // Создаем CodeLens для функций
            for (const func of functions) {
                const suggestions = await this.ragService.getFunctionSuggestions(func.name, func.context);
                
                if (suggestions && suggestions.length > 0) {
                    const codeLens = new vscode.CodeLens(func.range);
                    codeLens.command = {
                        title: `🤖 AI: ${suggestions.length} suggestion(s)`,
                        command: 'rag-extension.showFunctionSuggestions',
                        arguments: [func, suggestions]
                    };
                    codeLenses.push(codeLens);
                }
            }
            
            // Создаем CodeLens для классов
            for (const cls of classes) {
                const improvements = await this.ragService.getClassImprovements(cls.name, cls.context);
                
                if (improvements && improvements.length > 0) {
                    const codeLens = new vscode.CodeLens(cls.range);
                    codeLens.command = {
                        title: `🔧 AI: ${improvements.length} improvement(s)`,
                        command: 'rag-extension.showClassImprovements',
                        arguments: [cls, improvements]
                    };
                    codeLenses.push(codeLens);
                }
            }
            
            return codeLenses;

        } catch (error) {
            console.error('Error providing code lenses:', error);
            return [];
        }
    }

    private extractFunctions(document: vscode.TextDocument): Array<{name: string, context: string, range: vscode.Range}> {
        const functions = [];
        const functionRegex = /(?:function\s+(\w+)|(\w+)\s*:\s*(?:async\s+)?\w+\s*=|(\w+)\s*\(\s*[^)]*\)\s*\{)/g;
        
        for (let i = 0; i < document.lineCount; i++) {
            const line = document.lineAt(i);
            const match = functionRegex.exec(line.text);
            
            if (match) {
                const functionName = match[1] || match[2] || match[3];
                if (functionName) {
                    const context = this.getFunctionContext(document, i);
                    functions.push({
                        name: functionName,
                        context: context,
                        range: line.range
                    });
                }
            }
        }
        
        return functions;
    }

    private extractClasses(document: vscode.TextDocument): Array<{name: string, context: string, range: vscode.Range}> {
        const classes = [];
        const classRegex = /(?:class\s+(\w+)|interface\s+(\w+)|type\s+(\w+)\s*=)/g;
        
        for (let i = 0; i < document.lineCount; i++) {
            const line = document.lineAt(i);
            const match = classRegex.exec(line.text);
            
            if (match) {
                const className = match[1] || match[2] || match[3];
                if (className) {
                    const context = this.getClassContext(document, i);
                    classes.push({
                        name: className,
                        context: context,
                        range: line.range
                    });
                }
            }
        }
        
        return classes;
    }

    private getFunctionContext(document: vscode.TextDocument, lineIndex: number): string {
        const startLine = Math.max(0, lineIndex - 2);
        const endLine = Math.min(document.lineCount - 1, lineIndex + 10);
        
        const contextLines = [];
        for (let i = startLine; i <= endLine; i++) {
            contextLines.push(document.lineAt(i).text);
        }
        
        return contextLines.join('\n');
    }

    private getClassContext(document: vscode.TextDocument, lineIndex: number): string {
        const startLine = Math.max(0, lineIndex - 2);
        const endLine = Math.min(document.lineCount - 1, lineIndex + 15);
        
        const contextLines = [];
        for (let i = startLine; i <= endLine; i++) {
            contextLines.push(document.lineAt(i).text);
        }
        
        return contextLines.join('\n');
    }
}
