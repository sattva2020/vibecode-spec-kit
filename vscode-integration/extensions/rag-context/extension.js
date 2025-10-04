const vscode = require('vscode');
const RAGClient = require('./src/ragClient');
const ContextProvider = require('./src/contextProvider');
const InlineCompletionProvider = require('./src/inlineCompletion');
const Commands = require('./src/commands');

let ragClient;
let contextProvider;
let statusBarItem;

function activate(context) {
    console.log('🚀 RAG Context Provider is now active!');

    // Инициализация RAG клиента
    const config = vscode.workspace.getConfiguration('rag');
    ragClient = new RAGClient(config.get('proxyUrl'));

    // Status bar
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = "$(database) RAG";
    statusBarItem.tooltip = "RAG Context Provider";
    statusBarItem.command = 'rag.searchContext';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Context Provider для AI
    contextProvider = new ContextProvider(ragClient);

    // Inline Completion Provider
    if (config.get('enableInlineCompletion')) {
        const inlineProvider = new InlineCompletionProvider(ragClient, contextProvider);
        context.subscriptions.push(
            vscode.languages.registerInlineCompletionItemProvider(
                { pattern: '**' },
                inlineProvider
            )
        );
    }

    // Команды
    const commands = new Commands(ragClient, contextProvider);
    
    context.subscriptions.push(
        vscode.commands.registerCommand('rag.searchContext', commands.searchContext.bind(commands)),
        vscode.commands.registerCommand('rag.indexFile', commands.indexFile.bind(commands)),
        vscode.commands.registerCommand('rag.indexWorkspace', commands.indexWorkspace.bind(commands)),
        vscode.commands.registerCommand('rag.getExamples', commands.getExamples.bind(commands)),
        vscode.commands.registerCommand('rag.triggerN8n', commands.triggerN8n.bind(commands)),
        vscode.commands.registerCommand('rag.explainCode', commands.explainCode.bind(commands)),
        vscode.commands.registerCommand('rag.refactorWithContext', commands.refactorWithContext.bind(commands))
    );

    // Auto-index on save
    if (config.get('autoIndex')) {
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(async (document) => {
                if (shouldIndexDocument(document)) {
                    await commands.indexFile();
                    updateStatusBar('✓ Indexed');
                }
            })
        );
    }

    // Copilot Chat Integration
    registerChatParticipant(context, ragClient, contextProvider);

    vscode.window.showInformationMessage('RAG Context Provider activated! 🎉');
}

function shouldIndexDocument(document) {
    const validExtensions = ['.js', '.ts', '.tsx', '.jsx', '.py', '.rs', '.go', '.java'];
    const ext = document.fileName.slice(document.fileName.lastIndexOf('.'));
    return validExtensions.includes(ext) && !document.fileName.includes('node_modules');
}

function updateStatusBar(text) {
    statusBarItem.text = `$(database) RAG ${text}`;
    setTimeout(() => {
        statusBarItem.text = "$(database) RAG";
    }, 2000);
}

function registerChatParticipant(context, ragClient, contextProvider) {
    const participant = vscode.chat.createChatParticipant('rag-assistant', async (request, chatContext, stream, token) => {
        // Получаем контекст из RAG
        const ragContext = await contextProvider.getContextForQuery(request.prompt);
        
        stream.markdown(`### 🔍 RAG Context Found:\n`);
        stream.markdown(`\`\`\`\n${ragContext.slice(0, 200)}...\n\`\`\`\n\n`);
        
        // Отправляем в Copilot с расширенным контекстом
        stream.markdown(`### 💡 Answer:\n`);
        stream.markdown(request.prompt);
        
        return { metadata: { ragContext } };
    });

    participant.iconPath = vscode.Uri.file('media/icon.png');
    context.subscriptions.push(participant);
}

function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
