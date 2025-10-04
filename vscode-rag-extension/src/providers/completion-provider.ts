import * as vscode from 'vscode';
import { RAGService } from '../services/rag-service';

export class AICompletionProvider implements vscode.InlineCompletionItemProvider {
    private ragService: RAGService;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.ragService = new RAGService();
    }

    async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | vscode.InlineCompletionList | null | undefined> {
        try {
            // Получаем контекст кода
            const codeContext = this.getCodeContext(document, position);
            
            // Запрашиваем AI предложения
            const suggestions = await this.ragService.getCodeSuggestions(codeContext);
            
            if (!suggestions || suggestions.length === 0) {
                return null;
            }

            // Преобразуем в InlineCompletionItem
            return suggestions.map(suggestion => {
                const item = new vscode.InlineCompletionItem(suggestion.text);
                item.insertText = suggestion.text;
                item.filterText = suggestion.filterText;
                item.range = suggestion.range;
                item.command = {
                    title: 'AI Suggestion',
                    command: 'rag-extension.acceptSuggestion',
                    arguments: [suggestion]
                };
                return item;
            });

        } catch (error) {
            console.error('Error providing AI completions:', error);
            return null;
        }
    }

    private getCodeContext(document: vscode.TextDocument, position: vscode.Position): string {
        const line = document.lineAt(position.line);
        const beforeCursor = line.text.substring(0, position.character);
        const afterCursor = line.text.substring(position.character);
        
        // Получаем контекст из нескольких строк вокруг текущей позиции
        const startLine = Math.max(0, position.line - 5);
        const endLine = Math.min(document.lineCount - 1, position.line + 5);
        
        const contextLines = [];
        for (let i = startLine; i <= endLine; i++) {
            contextLines.push(document.lineAt(i).text);
        }
        
        return contextLines.join('\n');
    }
}
