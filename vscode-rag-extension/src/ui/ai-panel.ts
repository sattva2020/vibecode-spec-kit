import * as vscode from 'vscode';
import { RAGService } from '../services/rag-service';

export class AIPanel {
    private panel: vscode.WebviewPanel | undefined;
    private ragService: RAGService;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.ragService = new RAGService();
    }

    public show() {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.Two);
            return;
        }

        this.panel = vscode.window.createWebviewPanel(
            'aiPanel',
            '🤖 RAG AI Assistant',
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        this.panel.webview.html = this.getWebviewContent();
        
        // Обработка сообщений от webview
        this.panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'analyzeCode':
                        await this.handleAnalyzeCode(message.text);
                        break;
                    case 'generateCode':
                        await this.handleGenerateCode(message.prompt);
                        break;
                    case 'explainCode':
                        await this.handleExplainCode(message.code);
                        break;
                    case 'optimizeCode':
                        await this.handleOptimizeCode(message.code);
                        break;
                }
            },
            undefined,
            this.context.subscriptions
        );

        this.panel.onDidDispose(() => {
            this.panel = undefined;
        });
    }

    private async handleAnalyzeCode(code: string) {
        try {
            const analysis = await this.ragService.analyzeCode({
                code,
                language: 'typescript',
                filePath: ''
            });
            this.sendMessageToWebview('analysisResult', analysis);
        } catch (error) {
            this.sendMessageToWebview('error', { message: 'Failed to analyze code' });
        }
    }

    private async handleGenerateCode(prompt: string) {
        try {
            const generatedCode = await this.ragService.generateCode(prompt);
            this.sendMessageToWebview('generatedCode', { code: generatedCode });
        } catch (error) {
            this.sendMessageToWebview('error', { message: 'Failed to generate code' });
        }
    }

    private async handleExplainCode(code: string) {
        try {
            const explanation = await this.ragService.explainCode({
                code,
                language: 'typescript',
                filePath: ''
            });
            this.sendMessageToWebview('explanation', explanation);
        } catch (error) {
            this.sendMessageToWebview('error', { message: 'Failed to explain code' });
        }
    }

    private async handleOptimizeCode(code: string) {
        try {
            const optimizedCode = await this.ragService.optimizeCode({
                code,
                language: 'typescript',
                filePath: ''
            });
            this.sendMessageToWebview('optimizedCode', { code: optimizedCode });
        } catch (error) {
            this.sendMessageToWebview('error', { message: 'Failed to optimize code' });
        }
    }

    private sendMessageToWebview(command: string, data: any) {
        if (this.panel) {
            this.panel.webview.postMessage({ command, data });
        }
    }

    private getWebviewContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG AI Assistant</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
            margin: 0;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background-color: var(--vscode-input-background);
            border-radius: 8px;
        }
        
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background-color: var(--vscode-input-background);
            border-radius: 8px;
            border: 1px solid var(--vscode-input-border);
        }
        
        .section h3 {
            margin-top: 0;
            color: var(--vscode-textLink-foreground);
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
        }
        
        textarea {
            height: 100px;
            resize: vertical;
        }
        
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: var(--vscode-font-size);
            margin-right: 10px;
        }
        
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            background-color: var(--vscode-button-secondaryBackground);
            cursor: not-allowed;
        }
        
        .result {
            margin-top: 15px;
            padding: 15px;
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textBlockQuote-border);
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: var(--vscode-editor-font-family);
        }
        
        .loading {
            text-align: center;
            color: var(--vscode-progressBar-background);
        }
        
        .error {
            color: var(--vscode-errorForeground);
            background-color: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
        }
        
        .success {
            color: var(--vscode-testing-iconPassed);
            background-color: var(--vscode-inputValidation-infoBackground);
            border: 1px solid var(--vscode-inputValidation-infoBorder);
        }
        
        .code-block {
            background-color: var(--vscode-textCodeBlock-background);
            border: 1px solid var(--vscode-textCodeBlock-border);
            border-radius: 4px;
            padding: 10px;
            font-family: var(--vscode-editor-font-family);
            white-space: pre-wrap;
            overflow-x: auto;
        }
        
        .copy-button {
            float: right;
            margin-top: 5px;
            padding: 5px 10px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 RAG AI Assistant</h1>
            <p>AI-powered code analysis, generation, and optimization</p>
        </div>
        
        <div class="section">
            <h3>📊 Code Analysis</h3>
            <div class="input-group">
                <label for="analysisCode">Paste your code for analysis:</label>
                <textarea id="analysisCode" placeholder="Paste your code here..."></textarea>
            </div>
            <button onclick="analyzeCode()">Analyze Code</button>
            <div id="analysisResult"></div>
        </div>
        
        <div class="section">
            <h3>✨ Code Generation</h3>
            <div class="input-group">
                <label for="generatePrompt">Describe what you want to generate:</label>
                <textarea id="generatePrompt" placeholder="e.g., Create a function that validates email addresses..."></textarea>
            </div>
            <button onclick="generateCode()">Generate Code</button>
            <div id="generatedCodeResult"></div>
        </div>
        
        <div class="section">
            <h3>📖 Code Explanation</h3>
            <div class="input-group">
                <label for="explainCode">Code to explain:</label>
                <textarea id="explainCode" placeholder="Paste code you want explained..."></textarea>
            </div>
            <button onclick="explainCode()">Explain Code</button>
            <div id="explanationResult"></div>
        </div>
        
        <div class="section">
            <h3>⚡ Code Optimization</h3>
            <div class="input-group">
                <label for="optimizeCode">Code to optimize:</label>
                <textarea id="optimizeCode" placeholder="Paste code you want to optimize..."></textarea>
            </div>
            <button onclick="optimizeCode()">Optimize Code</button>
            <div id="optimizedCodeResult"></div>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function analyzeCode() {
            const code = document.getElementById('analysisCode').value;
            if (!code.trim()) {
                showResult('analysisResult', 'Please enter some code to analyze.', 'error');
                return;
            }
            
            showLoading('analysisResult');
            vscode.postMessage({
                command: 'analyzeCode',
                text: code
            });
        }
        
        function generateCode() {
            const prompt = document.getElementById('generatePrompt').value;
            if (!prompt.trim()) {
                showResult('generatedCodeResult', 'Please enter a description of what you want to generate.', 'error');
                return;
            }
            
            showLoading('generatedCodeResult');
            vscode.postMessage({
                command: 'generateCode',
                prompt: prompt
            });
        }
        
        function explainCode() {
            const code = document.getElementById('explainCode').value;
            if (!code.trim()) {
                showResult('explanationResult', 'Please enter some code to explain.', 'error');
                return;
            }
            
            showLoading('explanationResult');
            vscode.postMessage({
                command: 'explainCode',
                code: code
            });
        }
        
        function optimizeCode() {
            const code = document.getElementById('optimizeCode').value;
            if (!code.trim()) {
                showResult('optimizedCodeResult', 'Please enter some code to optimize.', 'error');
                return;
            }
            
            showLoading('optimizedCodeResult');
            vscode.postMessage({
                command: 'optimizeCode',
                code: code
            });
        }
        
        function showLoading(elementId) {
            document.getElementById(elementId).innerHTML = '<div class="loading">🤖 AI is thinking...</div>';
        }
        
        function showResult(elementId, content, type = 'result') {
            const element = document.getElementById(elementId);
            if (type === 'result') {
                element.innerHTML = \`<div class="result \${type}">\${content}</div>\`;
            } else {
                element.innerHTML = \`<div class="\${type}">\${content}</div>\`;
            }
        }
        
        function showCodeResult(elementId, code, title) {
            const element = document.getElementById(elementId);
            element.innerHTML = \`
                <div class="result success">
                    <strong>\${title}</strong>
                    <button class="copy-button" onclick="copyToClipboard('\${code.replace(/'/g, "\\'")}')">Copy</button>
                    <div class="code-block">\${code}</div>
                </div>
            \`;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                // Show brief success message
                const button = event.target;
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 1000);
            });
        }
        
        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'analysisResult':
                    showResult('analysisResult', JSON.stringify(message.data, null, 2));
                    break;
                case 'generatedCode':
                    showCodeResult('generatedCodeResult', message.data.code, 'Generated Code:');
                    break;
                case 'explanation':
                    showResult('explanationResult', message.data);
                    break;
                case 'optimizedCode':
                    showCodeResult('optimizedCodeResult', message.data.code, 'Optimized Code:');
                    break;
                case 'error':
                    showResult('analysisResult', message.data.message, 'error');
                    showResult('generatedCodeResult', message.data.message, 'error');
                    showResult('explanationResult', message.data.message, 'error');
                    showResult('optimizedCodeResult', message.data.message, 'error');
                    break;
            }
        });
    </script>
</body>
</html>`;
    }
}
