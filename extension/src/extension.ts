import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Memory Bank Configuration Interface
 */
interface MemoryBankConfig {
  language: string;
  defaultComplexity: string;
  autoSave: boolean;
  templatesPath: string;
}

/**
 * Memory Bank Detection Result
 */
interface MemoryBankDetection {
  exists: boolean;
  path?: string;
  reason?: string;
}

/**
 * Extension activation function
 * Implements hybrid activation strategy:
 * - onStartupFinished: Proactive detection after VS Code ready
 * - onCommand: Commands always available via Command Palette
 */
export function activate(context: vscode.ExtensionContext) {
  console.log('Memory Bank extension activating...');

  // Detect Memory Bank on startup (hybrid activation strategy)
  const detection = detectMemoryBank();
  
  if (detection.exists) {
    console.log(`Memory Bank detected at: ${detection.path}`);
    showStatusBarItem(context, true);
  } else {
    console.log(`Memory Bank not detected: ${detection.reason}`);
    showStatusBarItem(context, false);
  }

  // Register all Memory Bank commands
  const commands = [
    { id: 'memoryBank.van', keyword: 'VAN' },
    { id: 'memoryBank.plan', keyword: 'PLAN' },
    { id: 'memoryBank.creative', keyword: 'CREATIVE' },
    { id: 'memoryBank.implement', keyword: 'IMPLEMENT' },
    { id: 'memoryBank.reflect', keyword: 'REFLECT' },
    { id: 'memoryBank.archive', keyword: 'ARCHIVE' },
    { id: 'memoryBank.sync', keyword: 'SYNC' },
    { id: 'memoryBank.setup', keyword: 'SETUP' },
    { id: 'memoryBank.status', keyword: 'STATUS' }
  ];

  commands.forEach(cmd => {
    const disposable = vscode.commands.registerCommand(cmd.id, () => {
      handleModeCommand(cmd.keyword);
    });
    context.subscriptions.push(disposable);
  });

  console.log('Memory Bank extension activated successfully');
}

/**
 * Extension deactivation function
 */
export function deactivate() {
  console.log('Memory Bank extension deactivated');
}

/**
 * Detect Memory Bank in workspace
 * Checks for .vscode/memory-bank/ directory
 */
function detectMemoryBank(): MemoryBankDetection {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  
  if (!workspaceFolders || workspaceFolders.length === 0) {
    return {
      exists: false,
      reason: 'No workspace folder open'
    };
  }

  // Check first workspace folder for Memory Bank
  const workspaceRoot = workspaceFolders[0].uri.fsPath;
  const memoryBankPath = path.join(workspaceRoot, '.vscode', 'memory-bank');

  if (fs.existsSync(memoryBankPath)) {
    return {
      exists: true,
      path: memoryBankPath
    };
  }

  return {
    exists: false,
    reason: 'Memory Bank directory not found (.vscode/memory-bank/)'
  };
}

/**
 * Load Memory Bank configuration from VS Code settings
 */
function loadConfig(): MemoryBankConfig {
  const config = vscode.workspace.getConfiguration('memoryBank');
  
  return {
    language: config.get<string>('language', 'en'),
    defaultComplexity: config.get<string>('defaultComplexity', 'Level 2'),
    autoSave: config.get<boolean>('autoSave', true),
    templatesPath: config.get<string>('templatesPath', '')
  };
}

/**
 * Handle mode command execution
 * Phase 1 MVP: Opens Copilot Chat panel and notifies about mode keyword
 */
function handleModeCommand(keyword: string) {
  const detection = detectMemoryBank();
  
  // Guard: Check Memory Bank exists
  if (!detection.exists) {
    vscode.window.showWarningMessage(
      `Memory Bank not detected. ${detection.reason}. Run "Memory Bank: Setup Wizard" to initialize.`,
      'Setup Wizard'
    ).then((selection: string | undefined) => {
      if (selection === 'Setup Wizard') {
        vscode.commands.executeCommand('memoryBank.setup');
      }
    });
    return;
  }

  // Special handling for setup and status commands
  if (keyword === 'SETUP') {
    handleSetupWizard();
    return;
  }

  if (keyword === 'STATUS') {
    handleShowStatus(detection);
    return;
  }

  // Phase 1 MVP Implementation:
  // 1. Open Copilot Chat panel
  // 2. Show notification with mode keyword
  
  // Open Copilot Chat (VS Code built-in command)
  vscode.commands.executeCommand('workbench.action.chat.open').then(() => {
    // Show information message with mode keyword
    vscode.window.showInformationMessage(
      `💡 Memory Bank: Type "${keyword}" in Copilot Chat to activate ${keyword} mode`,
      'Got it'
    );
  }, (error: Error) => {
    vscode.window.showErrorMessage(
      `Failed to open Copilot Chat: ${error.message}`
    );
  });
}

/**
 * Handle setup wizard command
 * Creates Memory Bank structure in workspace
 */
function handleSetupWizard() {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  
  if (!workspaceFolders || workspaceFolders.length === 0) {
    vscode.window.showErrorMessage('Please open a workspace folder first');
    return;
  }

  const workspaceRoot = workspaceFolders[0].uri.fsPath;
  const memoryBankPath = path.join(workspaceRoot, '.vscode', 'memory-bank');

  // Check if already exists
  if (fs.existsSync(memoryBankPath)) {
    vscode.window.showInformationMessage('Memory Bank already initialized in this workspace');
    return;
  }

  // Show progress
  vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: 'Setting up Memory Bank...',
      cancellable: false
    },
    async (progress: { report: (value: { increment?: number; message?: string }) => void }) => {
      progress.report({ increment: 0, message: 'Creating directories...' });
      
      // Create directories
      fs.mkdirSync(memoryBankPath, { recursive: true });
      fs.mkdirSync(path.join(memoryBankPath, 'creative'), { recursive: true });
      fs.mkdirSync(path.join(memoryBankPath, 'reflection'), { recursive: true });
      fs.mkdirSync(path.join(memoryBankPath, 'archive'), { recursive: true });
      
      progress.report({ increment: 30, message: 'Detecting language preference...' });
      
      // Detect system language
      const systemLanguage = vscode.env.language; // e.g., "en", "ru-RU"
      const languageCode = systemLanguage.split('-')[0]; // Extract "ru" from "ru-RU"
      
      // Write .language file
      fs.writeFileSync(path.join(memoryBankPath, '.language'), languageCode);
      
      progress.report({ increment: 50, message: 'Creating template files...' });
      
      // Create initial template files (basic structure)
      createInitialTemplates(memoryBankPath);
      
      progress.report({ increment: 100, message: 'Complete!' });
      
      return new Promise(resolve => setTimeout(resolve, 500));
    }
  ).then(() => {
    vscode.window.showInformationMessage(
      '✅ Memory Bank initialized successfully! Type "VAN" in Copilot Chat to start.',
      'Open Chat'
    ).then((selection: string | undefined) => {
      if (selection === 'Open Chat') {
        vscode.commands.executeCommand('workbench.action.chat.open');
      }
    });
  });
}

/**
 * Create initial Memory Bank template files
 */
function createInitialTemplates(memoryBankPath: string) {
  const config = loadConfig();
  
  // tasks.md
  const tasksContent = `# Memory Bank: Task Tracking

> Single source of truth for all development tasks

## Active Tasks

(No tasks yet. Type "VAN" in Copilot Chat to create your first task!)

---

## Completed Tasks

(Completed tasks will appear here)
`;
  fs.writeFileSync(path.join(memoryBankPath, 'tasks.md'), tasksContent);

  // activeContext.md
  const activeContextContent = `# Memory Bank: Active Context

> **Latest Update:** ${new Date().toISOString().split('T')[0]}

## Current Focus

- **Mode:** Ready to start
- **Status:** Memory Bank initialized
- **Next Step:** Type "VAN" in Copilot Chat to assess your first task

---

## Latest Changes

- **${new Date().toISOString().split('T')[0]}**: Memory Bank initialized via Setup Wizard

---

## Immediate Next Steps

1. **Type "VAN"** in Copilot Chat to create your first task
2. Review Memory Bank structure in \`.vscode/memory-bank/\`
3. Check settings in VS Code: Memory Bank → Language, Complexity, etc.
`;
  fs.writeFileSync(path.join(memoryBankPath, 'activeContext.md'), activeContextContent);

  // progress.md
  const progressContent = `# Memory Bank: Implementation Progress

> Record implementation activity with absolute paths, key changes, and testing notes.

## ${new Date().toISOString().split('T')[0]}: Memory Bank Initialization

**Setup completed via Setup Wizard**

**Files Created:**
- \`${path.join(memoryBankPath, 'tasks.md')}\` - Task tracking
- \`${path.join(memoryBankPath, 'activeContext.md')}\` - Current focus
- \`${path.join(memoryBankPath, 'progress.md')}\` - This file
- \`${path.join(memoryBankPath, '.language')}\` - Language preference (${config.language})

**Next Steps:**
- Type "VAN" in Copilot Chat to create first task
- Explore Memory Bank modes (PLAN, CREATIVE, IMPLEMENT, REFLECT, ARCHIVE, SYNC)

---
`;
  fs.writeFileSync(path.join(memoryBankPath, 'progress.md'), progressContent);

  // projectbrief.md
  const projectBriefContent = `# Memory Bank: Project Brief

> Project overview and architecture

## Project Name

[Your project name]

## Description

[Brief description of your project]

## Technology Stack

- [Technology 1]
- [Technology 2]
- [Technology 3]

## Architecture

[Describe your project architecture]

## Goals

1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

---

**Created:** ${new Date().toISOString().split('T')[0]}  
**Last Updated:** ${new Date().toISOString().split('T')[0]}
`;
  fs.writeFileSync(path.join(memoryBankPath, 'projectbrief.md'), projectBriefContent);
}

/**
 * Handle show status command
 * Displays Memory Bank status in Output Channel
 */
function handleShowStatus(detection: MemoryBankDetection) {
  const config = loadConfig();
  
  // Create or get output channel
  const outputChannel = vscode.window.createOutputChannel('Memory Bank Status');
  outputChannel.clear();
  outputChannel.show();
  
  outputChannel.appendLine('═══════════════════════════════════════════');
  outputChannel.appendLine('  Memory Bank Status');
  outputChannel.appendLine('═══════════════════════════════════════════');
  outputChannel.appendLine('');
  
  if (detection.exists) {
    outputChannel.appendLine('✅ Memory Bank: ACTIVE');
    outputChannel.appendLine(`📁 Location: ${detection.path}`);
  } else {
    outputChannel.appendLine('❌ Memory Bank: NOT DETECTED');
    outputChannel.appendLine(`   Reason: ${detection.reason}`);
  }
  
  outputChannel.appendLine('');
  outputChannel.appendLine('───────────────────────────────────────────');
  outputChannel.appendLine('  Configuration');
  outputChannel.appendLine('───────────────────────────────────────────');
  outputChannel.appendLine(`🌐 Language: ${config.language}`);
  outputChannel.appendLine(`📊 Default Complexity: ${config.defaultComplexity}`);
  outputChannel.appendLine(`💾 Auto-Save: ${config.autoSave ? 'Enabled' : 'Disabled'}`);
  outputChannel.appendLine(`📂 Templates Path: ${config.templatesPath || '(default)'}`);
  
  outputChannel.appendLine('');
  outputChannel.appendLine('───────────────────────────────────────────');
  outputChannel.appendLine('  Available Modes');
  outputChannel.appendLine('───────────────────────────────────────────');
  outputChannel.appendLine('• VAN      - Project initialization');
  outputChannel.appendLine('• PLAN     - Task planning');
  outputChannel.appendLine('• CREATIVE - Design exploration');
  outputChannel.appendLine('• IMPLEMENT - Step-by-step implementation');
  outputChannel.appendLine('• REFLECT  - Review and retrospective');
  outputChannel.appendLine('• ARCHIVE  - Documentation finalization');
  outputChannel.appendLine('• SYNC     - System diagnostics');
  outputChannel.appendLine('');
  outputChannel.appendLine('═══════════════════════════════════════════');
}

/**
 * Show/hide status bar item based on Memory Bank detection
 */
function showStatusBarItem(context: vscode.ExtensionContext, memoryBankActive: boolean) {
  const statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100
  );
  
  if (memoryBankActive) {
    statusBarItem.text = '$(database) Memory Bank';
    statusBarItem.tooltip = 'Memory Bank Active - Click for status';
    statusBarItem.command = 'memoryBank.status';
    statusBarItem.show();
  } else {
    statusBarItem.text = '$(warning) Memory Bank';
    statusBarItem.tooltip = 'Memory Bank Not Detected - Click to setup';
    statusBarItem.command = 'memoryBank.setup';
    statusBarItem.show();
  }
  
  context.subscriptions.push(statusBarItem);
}
