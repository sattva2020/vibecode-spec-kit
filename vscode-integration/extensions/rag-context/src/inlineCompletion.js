const vscode = require('vscode');

class InlineCompletionProvider {
    constructor(ragClient, contextProvider) {
        this.ragClient = ragClient;
        this.contextProvider = contextProvider;
        this.completionCache = new Map();
    }

    async provideInlineCompletionItems(document, position, context, token) {
        try {
            // Получаем контекст вокруг позиции курсора
            const textBeforeCursor = document.getText(
                new vscode.Range(
                    new vscode.Position(Math.max(0, position.line - 10), 0),
                    position
                )
            );

            // Проверяем кеш
            const cacheKey = this.getCacheKey(textBeforeCursor);
            if (this.completionCache.has(cacheKey)) {
                return [this.completionCache.get(cacheKey)];
            }

            // Получаем контекст из RAG
            const ragContext = await this.contextProvider.getContextForQuery(
                `Complete this code: ${textBeforeCursor.slice(-200)}`
            );

            // Генерируем предложение на основе контекста
            const suggestion = this.generateSuggestion(textBeforeCursor, ragContext);

            if (suggestion) {
                const completion = new vscode.InlineCompletionItem(suggestion);
                this.completionCache.set(cacheKey, completion);
                return [completion];
            }

            return [];
        } catch (error) {
            console.error('Inline completion error:', error);
            return [];
        }
    }

    getCacheKey(text) {
        // Создаем простой хеш для кеширования
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            const char = text.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString();
    }

    generateSuggestion(code, context) {
        // Простая логика генерации предложений на основе контекста
        // В реальной реализации здесь был бы вызов LLM API
        
        const lines = code.split('\n');
        const lastLine = lines[lines.length - 1];
        
        // Анализируем последнюю строку
        if (lastLine.includes('function') || lastLine.includes('const') || lastLine.includes('let')) {
            return ' {\n    // TODO: Implement\n}';
        }
        
        if (lastLine.includes('if') || lastLine.includes('for') || lastLine.includes('while')) {
            return ' {\n    // TODO: Add logic\n}';
        }
        
        if (lastLine.includes('import') || lastLine.includes('require')) {
            return ';';
        }
        
        return null;
    }
}

module.exports = InlineCompletionProvider;
