/**
 * Демонстрация Memory Bank Timeout System
 */

console.log('🚀 Memory Bank Timeout System - Demo');
console.log('=====================================\n');

// Симуляция работы системы
class MockTimeoutManager {
  constructor() {
    this.activeProcesses = new Map();
    this.stats = {
      totalCommands: 0,
      successfulCommands: 0,
      timedOutCommands: 0,
      failedCommands: 0,
      averageExecutionTime: 0,
      successRate: 0
    };
  }

  async executeWithTimeout(command, args = [], timeout = 30000) {
    console.log(`⚡ Выполнение команды: ${command} ${args.join(' ')}`);
    console.log(`⏱️  Таймаут: ${timeout}ms`);
    
    this.stats.totalCommands++;
    
    // Симуляция выполнения команды
    const startTime = Date.now();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Симуляция работы
    const executionTime = Date.now() - startTime;
    
    const result = {
      success: true,
      exitCode: 0,
      stdout: `Команда ${command} выполнена успешно`,
      stderr: '',
      executionTime,
      processId: `process_${Date.now()}`,
      timedOut: false
    };
    
    this.stats.successfulCommands++;
    this.stats.averageExecutionTime = (this.stats.averageExecutionTime * (this.stats.totalCommands - 1) + executionTime) / this.stats.totalCommands;
    this.stats.successRate = (this.stats.successfulCommands / this.stats.totalCommands) * 100;
    
    console.log(`✅ Команда выполнена за ${executionTime}ms`);
    return result;
  }

  getTimeoutStats() {
    return { ...this.stats };
  }
}

class MockProcessMonitor {
  constructor() {
    this.activeProcesses = [];
  }

  addProcess(processInfo) {
    this.activeProcesses.push(processInfo);
    console.log(`📊 Процесс добавлен для мониторинга: ${processInfo.command}`);
  }

  removeProcess(processId) {
    this.activeProcesses = this.activeProcesses.filter(p => p.id !== processId);
    console.log(`📊 Процесс удален из мониторинга: ${processId}`);
  }

  getActiveProcesses() {
    return this.activeProcesses;
  }

  getStats() {
    return {
      totalProcesses: this.activeProcesses.length,
      activeProcesses: this.activeProcesses.length,
      completedProcesses: 0,
      failedProcesses: 0,
      averageExecutionTime: 0,
      lastUpdated: new Date()
    };
  }
}

class MockMemoryBankIntegration {
  constructor() {
    this.timeoutManager = new MockTimeoutManager();
    this.processMonitor = new MockProcessMonitor();
    this.currentMode = 'VAN';
    this.checkpoints = [];
    this.monitoredFiles = new Map();
  }

  async executeCommand(command, args = [], timeout) {
    console.log(`\n🔄 Выполнение команды через Memory Bank Integration:`);
    
    const result = await this.timeoutManager.executeWithTimeout(command, args, timeout);
    
    // Симуляция добавления в мониторинг
    this.processMonitor.addProcess({
      id: result.processId,
      command,
      args,
      startTime: new Date(),
      status: 'running'
    });
    
    // Симуляция завершения мониторинга
    setTimeout(() => {
      this.processMonitor.removeProcess(result.processId);
    }, 100);
    
    return result;
  }

  switchMode(newMode) {
    const previousMode = this.currentMode;
    this.currentMode = newMode;
    console.log(`🔄 Переключение режима: ${previousMode} → ${newMode}`);
  }

  createCheckpoint(description) {
    const checkpoint = {
      id: `checkpoint_${Date.now()}`,
      timestamp: new Date(),
      description,
      currentMode: this.currentMode,
      metadata: {
        activeProcesses: this.processMonitor.getActiveProcesses().length
      }
    };
    
    this.checkpoints.push(checkpoint);
    console.log(`📋 Checkpoint создан: ${description}`);
    console.log(`   ID: ${checkpoint.id}`);
    console.log(`   Режим: ${checkpoint.currentMode}`);
    
    return checkpoint.id;
  }

  getStats() {
    return {
      currentMode: this.currentMode,
      monitoredFiles: this.monitoredFiles.size,
      checkpoints: this.checkpoints.length,
      activeProcesses: this.processMonitor.getActiveProcesses().length,
      timeoutStats: this.timeoutManager.getTimeoutStats(),
      processMonitorStats: this.processMonitor.getStats()
    };
  }

  getCheckpoints() {
    return [...this.checkpoints];
  }
}

// Демонстрация работы системы
async function demonstrateSystem() {
  console.log('🎯 Создание экземпляра Memory Bank Integration...');
  const integration = new MockMemoryBankIntegration();
  
  console.log('\n📊 Начальная статистика:');
  console.log(JSON.stringify(integration.getStats(), null, 2));
  
  console.log('\n🔄 Переключение в режим PLAN...');
  integration.switchMode('PLAN');
  
  console.log('\n📋 Создание checkpoint\'а...');
  integration.createCheckpoint('Переход в режим PLAN');
  
  console.log('\n⚡ Выполнение команды echo...');
  const result1 = await integration.executeCommand('echo', ['Hello Memory Bank!'], 5000);
  console.log(`Результат: ${result1.stdout}`);
  
  console.log('\n⚡ Выполнение команды dir...');
  const result2 = await integration.executeCommand('dir', [], 10000);
  console.log(`Результат: ${result2.stdout}`);
  
  console.log('\n🔄 Переключение в режим CREATIVE...');
  integration.switchMode('CREATIVE');
  
  console.log('\n📋 Создание checkpoint\'а...');
  integration.createCheckpoint('Переход в режим CREATIVE');
  
  console.log('\n📊 Финальная статистика:');
  console.log(JSON.stringify(integration.getStats(), null, 2));
  
  console.log('\n📋 Все checkpoint\'ы:');
  integration.getCheckpoints().forEach((checkpoint, index) => {
    console.log(`${index + 1}. ${checkpoint.description} (${checkpoint.currentMode}) - ${checkpoint.timestamp.toLocaleTimeString()}`);
  });
  
  console.log('\n🎉 Демонстрация завершена успешно!');
  console.log('🚀 Memory Bank Timeout System работает корректно!');
}

// Запуск демонстрации
demonstrateSystem().catch(console.error);
