import * as vscode from 'vscode';
import { RAGService } from '../services/rag-service';

export class AIHoverProvider implements vscode.HoverProvider {
    private ragService: RAGService;

    constructor() {
        this.ragService = new RAGService();
    }

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | null | undefined> {
        try {
            // Получаем слово под курсором
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) {
                return null;
            }

            const word = document.getText(wordRange);
            
            // Получаем контекст функции/класса
            const codeContext = this.getCodeContext(document, position);
            
            // Запрашиваем объяснение от AI
            const explanation = await this.ragService.getCodeExplanation(word, codeContext);
            
            if (!explanation) {
                return null;
            }

            // Создаем Markdown содержимое для hover
            const markdownContent = new vscode.MarkdownString();
            markdownContent.isTrusted = true;
            
            markdownContent.appendMarkdown(`## 🤖 AI Explanation: \`${word}\`\n\n`);
            markdownContent.appendMarkdown(explanation.description);
            
            if (explanation.examples && explanation.examples.length > 0) {
                markdownContent.appendMarkdown('\n\n### Examples:\n');
                explanation.examples.forEach((example: any, index: number) => {
                    markdownContent.appendCodeblock(example.code, 'typescript');
                });
            }
            
            if (explanation.relatedConcepts && explanation.relatedConcepts.length > 0) {
                markdownContent.appendMarkdown('\n\n### Related Concepts:\n');
                explanation.relatedConcepts.forEach((concept: string) => {
                    markdownContent.appendMarkdown(`- ${concept}\n`);
                });
            }

            return new vscode.Hover(markdownContent, wordRange);

        } catch (error) {
            console.error('Error providing AI hover:', error);
            return null;
        }
    }

    private getCodeContext(document: vscode.TextDocument, position: vscode.Position): string {
        // Получаем контекст функции или класса
        const line = document.lineAt(position.line);
        
        // Ищем начало функции/класса
        let startLine = position.line;
        while (startLine >= 0) {
            const currentLine = document.lineAt(startLine).text;
            if (currentLine.includes('function') || currentLine.includes('class') || currentLine.includes('interface')) {
                break;
            }
            startLine--;
        }
        
        // Получаем несколько строк контекста
        const endLine = Math.min(document.lineCount - 1, position.line + 10);
        const contextLines = [];
        
        for (let i = Math.max(0, startLine); i <= endLine; i++) {
            contextLines.push(document.lineAt(i).text);
        }
        
        return contextLines.join('\n');
    }
}
