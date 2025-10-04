const vscode = require('vscode');

class Commands {
    constructor(ragClient, contextProvider) {
        this.ragClient = ragClient;
        this.contextProvider = contextProvider;
    }

    async searchContext() {
        try {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter your search query for RAG context',
                placeHolder: 'e.g., authentication patterns, database queries...'
            });

            if (!query) return;

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Searching RAG context...",
                cancellable: false
            }, async (progress) => {
                const result = await this.ragClient.searchContext(query);
                
                // Открываем результаты в новом документе
                const doc = await vscode.workspace.openTextDocument({
                    content: `# RAG Context Search Results\n\n**Query:** ${query}\n\n**Context:**\n${result.rag_context}\n\n**Database Schema:**\n${JSON.stringify(result.database_schema, null, 2)}`,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);
            });

        } catch (error) {
            vscode.window.showErrorMessage(`RAG search failed: ${error.message}`);
        }
    }

    async indexFile() {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor found');
                return;
            }

            const document = editor.document;
            const content = document.getText();
            
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Indexing current file...",
                cancellable: false
            }, async () => {
                await this.ragClient.indexContent(
                    content,
                    document.fileName,
                    {
                        language: document.languageId,
                        lastModified: new Date().toISOString()
                    }
                );
            });

            vscode.window.showInformationMessage(`✓ File indexed: ${document.fileName}`);

        } catch (error) {
            vscode.window.showErrorMessage(`Indexing failed: ${error.message}`);
        }
    }

    async indexWorkspace() {
        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Indexing entire workspace...",
                cancellable: false
            }, async () => {
                await this.contextProvider.indexCurrentWorkspace();
            });

            vscode.window.showInformationMessage('✓ Workspace indexed successfully');

        } catch (error) {
            vscode.window.showErrorMessage(`Workspace indexing failed: ${error.message}`);
        }
    }

    async getExamples() {
        try {
            const topic = await vscode.window.showInputBox({
                prompt: 'Enter topic for code examples',
                placeHolder: 'e.g., React hooks, authentication, database queries...'
            });

            if (!topic) return;

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Fetching code examples...",
                cancellable: false
            }, async () => {
                const examples = await this.ragClient.getExamples(topic);
                
                if (examples.length === 0) {
                    vscode.window.showInformationMessage(`No examples found for topic: ${topic}`);
                    return;
                }

                // Отображаем примеры в новом документе
                const content = `# Code Examples: ${topic}\n\n${examples.map((ex, i) => 
                    `## Example ${i + 1}\n\`\`\`${ex.language}\n${ex.code}\n\`\`\`\n${ex.description || ''}\n`
                ).join('\n')}`;

                const doc = await vscode.workspace.openTextDocument({
                    content,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get examples: ${error.message}`);
        }
    }

    async triggerN8n() {
        try {
            const workflowId = await vscode.window.showInputBox({
                prompt: 'Enter n8n workflow ID',
                placeHolder: 'e.g., setup-auth, deploy-app...'
            });

            if (!workflowId) return;

            const payloadStr = await vscode.window.showInputBox({
                prompt: 'Enter payload (JSON format)',
                placeHolder: '{"key": "value"} or leave empty for default'
            });

            const payload = payloadStr ? JSON.parse(payloadStr) : {};

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Triggering n8n workflow...",
                cancellable: false
            }, async () => {
                const result = await this.ragClient.triggerWorkflow(workflowId, payload);
                
                // Показываем результат
                const doc = await vscode.workspace.openTextDocument({
                    content: `# n8n Workflow Result\n\n**Workflow ID:** ${workflowId}\n\n**Result:**\n${JSON.stringify(result, null, 2)}`,
                    language: 'json'
                });
                
                await vscode.window.showTextDocument(doc);
            });

        } catch (error) {
            vscode.window.showErrorMessage(`n8n trigger failed: ${error.message}`);
        }
    }

    async explainCode() {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            if (selection.isEmpty) {
                vscode.window.showWarningMessage('Please select code to explain');
                return;
            }

            const selectedCode = editor.document.getText(selection);

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Explaining code with RAG context...",
                cancellable: false
            }, async () => {
                // Получаем контекст для объяснения кода
                const context = await this.contextProvider.getContextForQuery(
                    `Explain this code: ${selectedCode}`
                );

                // Открываем объяснение в новом документе
                const doc = await vscode.workspace.openTextDocument({
                    content: `# Code Explanation\n\n**Selected Code:**\n\`\`\`${editor.document.languageId}\n${selectedCode}\n\`\`\`\n\n**Explanation (with RAG context):**\n${context}`,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Code explanation failed: ${error.message}`);
        }
    }

    async refactorWithContext() {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            if (selection.isEmpty) {
                vscode.window.showWarningMessage('Please select code to refactor');
                return;
            }

            const selectedCode = editor.document.getText(selection);

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Refactoring code with RAG context...",
                cancellable: false
            }, async () => {
                // Получаем контекст для рефакторинга
                const context = await this.contextProvider.getContextForQuery(
                    `Refactor this code with best practices: ${selectedCode}`
                );

                // Открываем предложения по рефакторингу в новом документе
                const doc = await vscode.workspace.openTextDocument({
                    content: `# Code Refactoring Suggestions\n\n**Original Code:**\n\`\`\`${editor.document.languageId}\n${selectedCode}\n\`\`\`\n\n**Refactoring Suggestions (with RAG context):**\n${context}`,
                    language: 'markdown'
                });
                
                await vscode.window.showTextDocument(doc);
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Code refactoring failed: ${error.message}`);
        }
    }
}

module.exports = Commands;
