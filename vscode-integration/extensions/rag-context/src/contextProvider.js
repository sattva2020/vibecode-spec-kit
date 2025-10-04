const vscode = require('vscode');

class ContextProvider {
    constructor(ragClient) {
        this.ragClient = ragClient;
        this.contextCache = new Map();
    }

    async getContextForQuery(query) {
        // Проверяем кеш
        if (this.contextCache.has(query)) {
            return this.contextCache.get(query);
        }

        // Получаем текущий файл и окружение
        const editor = vscode.window.activeTextEditor;
        const currentFile = editor ? editor.document.getText() : '';
        const fileName = editor ? editor.document.fileName : '';

        // Расширенный запрос с контекстом
        const enrichedQuery = `
File: ${fileName}
Current code snippet:
${currentFile.slice(0, 500)}

User query: ${query}
        `;

        // Запрос к RAG
        const ragResult = await this.ragClient.searchContext(enrichedQuery);
        const context = ragResult.rag_context;

        // Кешируем
        this.contextCache.set(query, context);

        return context;
    }

    async getRelevantExamples(topic) {
        try {
            return await this.ragClient.getExamples(topic, 5);
        } catch (error) {
            console.error('Error getting examples:', error);
            return [];
        }
    }

    async indexCurrentWorkspace() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder found');
        }

        const files = await vscode.workspace.findFiles(
            '**/*.{js,ts,tsx,jsx,py,rs,go,java}',
            '**/node_modules/**'
        );

        for (const file of files) {
            try {
                const document = await vscode.workspace.openTextDocument(file);
                const content = document.getText();
                
                await this.ragClient.indexContent(
                    content,
                    file.fsPath,
                    {
                        language: document.languageId,
                        lastModified: document.uri.fsPath
                    }
                );
            } catch (error) {
                console.error(`Error indexing ${file.fsPath}:`, error);
            }
        }
    }

    clearCache() {
        this.contextCache.clear();
    }
}

module.exports = ContextProvider;
