import * as vscode from 'vscode';
import axios from 'axios';

interface RAGConfig {
    apiUrl: string;
    autoIndex: boolean;
    suggestions: boolean;
}

interface CodeSuggestion {
    text: string;
    confidence: number;
    type: string;
    source?: string;
}

class RAGContextProvider {
    private config: RAGConfig;
    private statusBarItem: vscode.StatusBarItem;
    private learningStatusItem: vscode.StatusBarItem;

    constructor() {
        this.config = this.loadConfig();
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.learningStatusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 99);
        
        this.setupStatusBar();
        this.setupEventListeners();
    }

    private loadConfig(): RAGConfig {
        const config = vscode.workspace.getConfiguration('ragContext');
        return {
            apiUrl: config.get('apiUrl', 'http://localhost:9000'), // Rust RAG Proxy endpoint
            autoIndex: config.get('autoIndex', true),
            suggestions: config.get('suggestions', true)
        };
    }

    private setupStatusBar() {
        this.statusBarItem.text = "$(brain) RAG";
        this.statusBarItem.tooltip = "RAG Context Provider - Click to show status";
        this.statusBarItem.command = 'rag-context.showLearningStatus';
        this.statusBarItem.show();

        this.learningStatusItem.text = "$(sync~spin) Learning";
        this.learningStatusItem.tooltip = "AI Learning Status";
        this.learningStatusItem.hide();
    }

    private setupEventListeners() {
        if (this.config.autoIndex) {
            vscode.workspace.onDidSaveTextDocument(async (document) => {
                if (this.shouldIndexDocument(document)) {
                    await this.indexDocument(document);
                }
            });
        }

        if (this.config.suggestions) {
            vscode.workspace.onDidChangeTextDocument(async (event) => {
                if (event.contentChanges.length > 0) {
                    await this.getSuggestions(event.document, event.contentChanges[0]);
                }
            });
        }
    }

    private shouldIndexDocument(document: vscode.TextDocument): boolean {
        const supportedLanguages = ['typescript', 'javascript', 'python', 'rust', 'go', 'java'];
        return supportedLanguages.includes(document.languageId) && 
               !document.fileName.includes('node_modules') &&
               !document.fileName.includes('.git');
    }

    private async indexDocument(document: vscode.TextDocument) {
        try {
            this.showLearningIndicator();
            
            const response = await axios.post(`${this.config.apiUrl}/api/learn`, {
                file_path: document.fileName,
                code: document.getText(),
                language: document.languageId,
                context: {
                    workspace: vscode.workspace.name,
                    timestamp: new Date().toISOString()
                }
            });

            if (response.status === 200) {
                vscode.window.showInformationMessage(`✅ Code indexed: ${document.fileName}`);
            }
        } catch (error) {
            console.error('Failed to index document:', error);
            vscode.window.showErrorMessage('Failed to index document for learning');
        } finally {
            this.hideLearningIndicator();
        }
    }

    private async getSuggestions(document: vscode.TextDocument, change: vscode.TextDocumentContentChangeEvent) {
        try {
            const response = await axios.post(`${this.config.apiUrl}/api/suggest`, {
                file_path: document.fileName,
                code: document.getText(),
                language: document.languageId,
                cursor_position: {
                    line: change.range.start.line,
                    character: change.range.start.character
                }
            });

            if (response.data.suggestions && response.data.suggestions.length > 0) {
                this.showSuggestions(response.data.suggestions);
            }
        } catch (error) {
            // Silently fail for suggestions to avoid spam
            console.error('Failed to get suggestions:', error);
        }
    }

    private showSuggestions(suggestions: CodeSuggestion[]) {
        if (suggestions.length === 0) return;

        const suggestion = suggestions[0];
        if (suggestion.confidence > 0.7) {
            vscode.window.showInformationMessage(
                `🤖 AI Suggestion: ${suggestion.text}`,
                'Accept',
                'Dismiss'
            ).then(selection => {
                if (selection === 'Accept') {
                    // Apply suggestion logic here
                    vscode.window.showInformationMessage('Suggestion accepted!');
                }
            });
        }
    }

    public async explainCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('Please select code to explain');
            return;
        }

        try {
            this.showLearningIndicator();
            
            const selectedCode = editor.document.getText(selection);
            const response = await axios.post(`${this.config.apiUrl}/api/context/search`, {
                query: `Explain this code: ${selectedCode}`,
                context: {
                    file_path: editor.document.fileName,
                    language: editor.document.languageId
                }
            });

            // Show explanation in a new document
            const explanationDoc = await vscode.workspace.openTextDocument({
                content: `# Code Explanation\n\n**Selected Code:**\n\`\`\`${editor.document.languageId}\n${selectedCode}\n\`\`\`\n\n**AI Explanation:**\n${response.data.result || 'No explanation available'}`,
                language: 'markdown'
            });

            await vscode.window.showTextDocument(explanationDoc);
        } catch (error) {
            vscode.window.showErrorMessage('Failed to explain code');
            console.error('Explain code error:', error);
        } finally {
            this.hideLearningIndicator();
        }
    }

    public async searchContext() {
        const query = await vscode.window.showInputBox({
            prompt: 'Search code context',
            placeHolder: 'Enter your search query...'
        });

        if (!query) return;

        try {
            this.showLearningIndicator();
            
            const response = await axios.post(`${this.config.apiUrl}/api/context/search`, {
                query: query
            });

            // Show search results in a new document
            const resultsDoc = await vscode.workspace.openTextDocument({
                content: `# Search Results\n\n**Query:** ${query}\n\n**Results:**\n${JSON.stringify(response.data, null, 2)}`,
                language: 'markdown'
            });

            await vscode.window.showTextDocument(resultsDoc);
        } catch (error) {
            vscode.window.showErrorMessage('Failed to search context');
            console.error('Search context error:', error);
        } finally {
            this.hideLearningIndicator();
        }
    }

    public async learnFromCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        await this.indexDocument(editor.document);
    }

    public async showLearningStatus() {
        try {
            const response = await axios.get(`${this.config.apiUrl}/health`);
            const status = response.data;

            const statusMessage = Object.entries(status.services)
                .map(([service, health]) => `${service}: ${health}`)
                .join('\n');

            vscode.window.showInformationMessage(
                `RAG System Status:\n${statusMessage}`,
                { modal: true }
            );
        } catch (error) {
            vscode.window.showErrorMessage('Failed to get system status');
        }
    }

    private showLearningIndicator() {
        this.learningStatusItem.show();
    }

    private hideLearningIndicator() {
        this.learningStatusItem.hide();
    }

    public dispose() {
        this.statusBarItem.dispose();
        this.learningStatusItem.dispose();
    }
}

let ragProvider: RAGContextProvider;

export function activate(context: vscode.ExtensionContext) {
    ragProvider = new RAGContextProvider();

    // Register commands
    const explainCommand = vscode.commands.registerCommand('rag-context.explainCode', () => {
        ragProvider.explainCode();
    });

    const searchCommand = vscode.commands.registerCommand('rag-context.searchContext', () => {
        ragProvider.searchContext();
    });

    const learnCommand = vscode.commands.registerCommand('rag-context.learnFromCode', () => {
        ragProvider.learnFromCode();
    });

    const statusCommand = vscode.commands.registerCommand('rag-context.showLearningStatus', () => {
        ragProvider.showLearningStatus();
    });

    context.subscriptions.push(explainCommand, searchCommand, learnCommand, statusCommand);

    vscode.window.showInformationMessage('🚀 RAG Context Provider activated!');
}

export function deactivate() {
    if (ragProvider) {
        ragProvider.dispose();
    }
}
