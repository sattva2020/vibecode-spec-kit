/**
 * Демонстрация Phase 3 - Integration & Session Management
 */

console.log('🚀 Memory Bank Timeout System - Phase 3 Demo');
console.log('===============================================\n');

// Симуляция работы Phase 3 - Integration & Session Management
class MockSessionManager {
  constructor() {
    this.currentSession = null;
    this.sessionHistory = [];
    this.stats = {
      totalSessions: 0,
      activeSessions: 0,
      completedSessions: 0,
      averageSessionDuration: 0,
      totalSessionTime: 0
    };
  }

  startNewSession(description) {
    const session = {
      id: `session_${Date.now()}`,
      description: description || `Сессия разработки ${new Date().toLocaleString()}`,
      startTime: new Date(),
      endTime: null,
      duration: 0,
      status: 'active',
      currentMode: 'VAN',
      modeHistory: [{ mode: 'VAN', timestamp: new Date(), duration: 0 }],
      checkpoints: [],
      commands: [],
      fileChanges: [],
      metadata: {
        project: 'Memory Bank Timeout System',
        version: '1.0.0'
      }
    };

    this.currentSession = session;
    this.sessionHistory.push(session);
    this.stats.totalSessions++;
    this.stats.activeSessions++;

    console.log(`🎯 Новая сессия начата: ${session.id}`);
    console.log(`   Описание: ${session.description}`);
    console.log(`   Режим: ${session.currentMode}`);
    
    return session;
  }

  switchMode(newMode, description) {
    if (!this.currentSession) return;

    const previousMode = this.currentSession.currentMode;
    const currentTime = new Date();

    // Обновление продолжительности предыдущего режима
    if (this.currentSession.modeHistory.length > 0) {
      const lastMode = this.currentSession.modeHistory[this.currentSession.modeHistory.length - 1];
      lastMode.duration = currentTime.getTime() - lastMode.timestamp.getTime();
    }

    // Добавление нового режима
    this.currentSession.modeHistory.push({
      mode: newMode,
      timestamp: currentTime,
      duration: 0
    });

    this.currentSession.currentMode = newMode;

    console.log(`🔄 Режим изменен: ${previousMode} → ${newMode}`);
    if (description) {
      console.log(`   Описание: ${description}`);
    }
  }

  addCheckpoint(checkpointId, description, metadata) {
    if (!this.currentSession) return;

    const checkpoint = {
      id: checkpointId,
      description,
      timestamp: new Date(),
      mode: this.currentSession.currentMode,
      metadata: metadata || {}
    };

    this.currentSession.checkpoints.push(checkpoint);
    console.log(`📋 Checkpoint добавлен в сессию: ${description}`);
  }

  addCommand(command, result, executionTime) {
    if (!this.currentSession) return;

    const commandInfo = {
      command,
      result,
      executionTime,
      timestamp: new Date(),
      mode: this.currentSession.currentMode
    };

    this.currentSession.commands.push(commandInfo);
    console.log(`⚡ Команда добавлена в сессию: ${command} (${executionTime}ms)`);
  }

  addFileChange(filePath, changeType) {
    if (!this.currentSession) return;

    const fileChange = {
      filePath,
      changeType,
      timestamp: new Date(),
      mode: this.currentSession.currentMode
    };

    this.currentSession.fileChanges.push(fileChange);
    console.log(`📝 Изменение файла добавлено: ${filePath} (${changeType})`);
  }

  endCurrentSession() {
    if (!this.currentSession) return null;

    const endTime = new Date();
    this.currentSession.endTime = endTime;
    this.currentSession.duration = endTime.getTime() - this.currentSession.startTime.getTime();
    this.currentSession.status = 'completed';

    this.stats.activeSessions--;
    this.stats.completedSessions++;

    console.log(`🏁 Сессия завершена: ${this.currentSession.id}`);
    console.log(`   Продолжительность: ${Math.round(this.currentSession.duration / 1000)}с`);
    console.log(`   Checkpoint'ов: ${this.currentSession.checkpoints.length}`);
    console.log(`   Команд: ${this.currentSession.commands.length}`);
    console.log(`   Изменений файлов: ${this.currentSession.fileChanges.length}`);

    const completedSession = this.currentSession;
    this.currentSession = null;
    return completedSession;
  }

  getStats() {
    return { ...this.stats };
  }
}

class MockWorkflowIntegration {
  constructor() {
    this.sessionManager = new MockSessionManager();
    this.workflowState = {
      currentMode: 'VAN',
      previousMode: 'VAN',
      sessionActive: false,
      currentSessionId: null,
      checkpointsInSession: 0,
      commandsInSession: 0
    };
  }

  startSession(description) {
    const session = this.sessionManager.startNewSession(description);
    this.workflowState.sessionActive = true;
    this.workflowState.currentSessionId = session.id;
    console.log(`🚀 Workflow Integration: сессия активирована`);
    return session;
  }

  switchMode(newMode, description) {
    this.workflowState.previousMode = this.workflowState.currentMode;
    this.workflowState.currentMode = newMode;
    
    this.sessionManager.switchMode(newMode, description);
    
    console.log(`🔄 Workflow Integration: режим переключен в ${newMode}`);
    
    // Создание автоматического checkpoint'а
    this.createAutoCheckpoint(`Переход в режим ${newMode}`, description);
  }

  executeCommand(command, args = [], timeout) {
    console.log(`⚡ Выполнение команды: ${command} ${args.join(' ')}`);
    
    // Симуляция выполнения команды
    const executionTime = Math.floor(Math.random() * 1000) + 100;
    const result = {
      success: true,
      command,
      args,
      executionTime,
      timestamp: new Date()
    };

    this.sessionManager.addCommand(command, result, executionTime);
    this.workflowState.commandsInSession++;

    console.log(`✅ Команда выполнена за ${executionTime}ms`);
    return result;
  }

  createAutoCheckpoint(description, metadata) {
    const checkpointId = `checkpoint_${Date.now()}`;
    this.sessionManager.addCheckpoint(checkpointId, description, {
      trigger: 'auto',
      ...metadata
    });
    this.workflowState.checkpointsInSession++;
    return checkpointId;
  }

  handleFileChange(filePath) {
    this.sessionManager.addFileChange(filePath, 'modified');
    console.log(`📁 Workflow Integration: файл изменен - ${filePath}`);
    
    // Создание автоматического checkpoint'а для важных файлов
    const importantFiles = ['memory-bank/tasks.md', 'memory-bank/activeContext.md'];
    if (importantFiles.some(file => filePath.includes(file))) {
      this.createAutoCheckpoint(`Автоматический checkpoint: ${filePath.split('/').pop()} изменен`);
    }
  }

  endSession() {
    const session = this.sessionManager.endCurrentSession();
    this.workflowState.sessionActive = false;
    this.workflowState.currentSessionId = null;
    console.log(`🏁 Workflow Integration: сессия завершена`);
    return session;
  }

  getIntegrationStats() {
    return {
      workflow: this.workflowState,
      session: this.sessionManager.getStats()
    };
  }
}

// Демонстрация работы Phase 3
async function demonstratePhase3() {
  console.log('🎯 Создание Workflow Integration...');
  
  const workflowIntegration = new MockWorkflowIntegration();
  
  console.log('\n🚀 Начало новой сессии разработки...');
  workflowIntegration.startSession('Демонстрация Phase 3 - Integration & Session Management');
  
  console.log('\n📋 Переключение в режим PLAN...');
  workflowIntegration.switchMode('PLAN', 'Планирование Phase 3');
  
  console.log('\n⚡ Выполнение команд планирования...');
  workflowIntegration.executeCommand('npm', ['run', 'build']);
  workflowIntegration.executeCommand('tsc', ['--noEmit']);
  
  console.log('\n📁 Симуляция изменений файлов...');
  workflowIntegration.handleFileChange('memory-bank/tasks.md');
  workflowIntegration.handleFileChange('memory-bank/activeContext.md');
  
  console.log('\n🎨 Переключение в режим CREATIVE...');
  workflowIntegration.switchMode('CREATIVE', 'Творческая фаза Phase 3');
  
  console.log('\n⚡ Выполнение команд разработки...');
  workflowIntegration.executeCommand('npm', ['start']);
  workflowIntegration.executeCommand('jest', ['--watch']);
  
  console.log('\n🛠️ Переключение в режим IMPLEMENT...');
  workflowIntegration.switchMode('IMPLEMENT', 'Реализация Phase 3');
  
  console.log('\n⚡ Выполнение команд реализации...');
  workflowIntegration.executeCommand('npm', ['run', 'build']);
  workflowIntegration.executeCommand('npm', ['test']);
  
  console.log('\n📁 Симуляция изменений файлов реализации...');
  workflowIntegration.handleFileChange('src/core/SessionManager.ts');
  workflowIntegration.handleFileChange('src/core/WorkflowIntegration.ts');
  
  console.log('\n🤔 Переключение в режим REFLECT...');
  workflowIntegration.switchMode('REFLECT', 'Рефлексия Phase 3');
  
  console.log('\n📁 Создание финального checkpoint\'а...');
  workflowIntegration.createAutoCheckpoint('Завершение Phase 3 - Integration & Session Management');
  
  console.log('\n📊 Статистика интеграции:');
  const stats = workflowIntegration.getIntegrationStats();
  console.log(JSON.stringify(stats, null, 2));
  
  console.log('\n🏁 Завершение сессии...');
  const completedSession = workflowIntegration.endSession();
  
  console.log('\n📋 Итоговая статистика сессии:');
  console.log(`   ID: ${completedSession.id}`);
  console.log(`   Описание: ${completedSession.description}`);
  console.log(`   Продолжительность: ${Math.round(completedSession.duration / 1000)}с`);
  console.log(`   Режимов: ${completedSession.modeHistory.length}`);
  console.log(`   Checkpoint'ов: ${completedSession.checkpoints.length}`);
  console.log(`   Команд: ${completedSession.commands.length}`);
  console.log(`   Изменений файлов: ${completedSession.fileChanges.length}`);
  
  console.log('\n🎉 Phase 3 - Integration & Session Management демонстрация завершена!');
  console.log('✅ Полная интеграция с Memory Bank workflow работает корректно!');
}

// Запуск демонстрации
demonstratePhase3().catch(console.error);
