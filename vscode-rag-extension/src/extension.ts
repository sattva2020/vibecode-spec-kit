import * as vscode from 'vscode';
import { AICompletionProvider, AIHoverProvider, AICodeLensProvider } from './providers';
import { AIPanel, QuickActions } from './ui';

export function activate(context: vscode.ExtensionContext) {
    console.log('🤖 RAG Extension is now active!');

    // Инициализируем сервисы
    const aiPanel = new AIPanel(context);
    const quickActions = new QuickActions(context);

    // Регистрируем провайдеры
    const completionProvider = new AICompletionProvider(context);
    const hoverProvider = new AIHoverProvider();
    const codeLensProvider = new AICodeLensProvider();

    // Регистрируем провайдеры в VS Code
    const completionDisposable = vscode.languages.registerInlineCompletionItemProvider(
        { scheme: 'file' },
        completionProvider
    );

    const hoverDisposable = vscode.languages.registerHoverProvider(
        { scheme: 'file' },
        hoverProvider
    );

    const codeLensDisposable = vscode.languages.registerCodeLensProvider(
        { scheme: 'file' },
        codeLensProvider
    );

    // Регистрируем команды
    const showAIPanelCommand = vscode.commands.registerCommand('rag-extension.showAIPanel', () => {
        aiPanel.show();
    });

    const refreshCodeLensesCommand = vscode.commands.registerCommand('rag-extension.refreshCodeLenses', () => {
        codeLensProvider.refresh();
    });

    // Регистрируем быстрые действия
    quickActions.registerCommands();

    // Добавляем в контекст подписки
    context.subscriptions.push(
        completionDisposable,
        hoverDisposable,
        codeLensDisposable,
        showAIPanelCommand,
        refreshCodeLensesCommand
    );

    // Показываем приветственное сообщение
    vscode.window.showInformationMessage(
        '🤖 RAG AI Extension activated! Use Ctrl+Shift+P and search for "RAG" to see available commands.',
        'Open AI Panel'
    ).then(selection => {
        if (selection === 'Open AI Panel') {
            aiPanel.show();
        }
    });

    // Автоматически обновляем CodeLens при изменении документа
    vscode.workspace.onDidChangeTextDocument(() => {
        codeLensProvider.refresh();
    });

    console.log('✅ RAG Extension initialization complete');
}

export function deactivate() {
    console.log('🤖 RAG Extension deactivated');
}