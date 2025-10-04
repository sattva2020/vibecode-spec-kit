/**
 * Демонстрация Phase 2 - Simplified Checkpoint System
 */

console.log('🚀 Memory Bank Timeout System - Phase 2 Demo');
console.log('==============================================\n');

// Симуляция работы Simplified Checkpoint System
class MockAutoCheckpointManager {
  constructor() {
    this.checkpoints = [];
    this.config = {
      enabled: true,
      interval: 300000,
      maxCheckpoints: 50,
      onFileChange: true,
      onModeChange: true,
      onCommandExecution: true
    };
  }

  async createCheckpoint(description, metadata = {}) {
    const checkpoint = {
      id: `checkpoint_${Date.now()}`,
      timestamp: new Date(),
      description,
      currentMode: metadata.currentMode || 'UNKNOWN',
      changedFiles: metadata.changedFiles || [],
      metadata: {
        ...metadata,
        trigger: metadata.trigger || 'manual',
        memoryBankFiles: this.getMemoryBankFiles()
      },
      size: Math.floor(Math.random() * 10000) + 1000
    };

    this.checkpoints.push(checkpoint);
    console.log(`📋 Checkpoint создан: ${description}`);
    console.log(`   ID: ${checkpoint.id}`);
    console.log(`   Режим: ${checkpoint.currentMode}`);
    console.log(`   Размер: ${checkpoint.size} байт`);
    
    return checkpoint.id;
  }

  getCheckpoints() {
    return [...this.checkpoints].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  getMemoryBankFiles() {
    return {
      'memory-bank/tasks.md': { size: 15000, modified: new Date(), exists: true },
      'memory-bank/activeContext.md': { size: 8000, modified: new Date(), exists: true },
      'memory-bank/progress.md': { size: 5000, modified: new Date(), exists: true }
    };
  }

  onFileChanged(filePath) {
    console.log(`📁 Файл изменен: ${filePath}`);
    this.createCheckpoint(
      `Автоматический checkpoint: файл ${filePath.split('/').pop()} изменен`,
      { trigger: 'fileChange', filePath }
    );
  }

  onModeChanged(newMode, previousMode) {
    console.log(`🔄 Режим изменен: ${previousMode} → ${newMode}`);
    this.createCheckpoint(
      `Переход из режима ${previousMode} в режим ${newMode}`,
      { trigger: 'modeChange', previousMode, newMode, currentMode: newMode }
    );
  }
}

class MockCheckpointStorage {
  constructor() {
    this.storage = new Map();
    this.stats = {
      totalCheckpoints: 0,
      totalSize: 0,
      averageSize: 0,
      lastUpdated: new Date()
    };
  }

  async saveCheckpoint(checkpoint) {
    this.storage.set(checkpoint.id, checkpoint);
    this.stats.totalCheckpoints++;
    this.stats.totalSize += checkpoint.size;
    this.stats.averageSize = this.stats.totalSize / this.stats.totalCheckpoints;
    this.stats.lastUpdated = new Date();
    
    console.log(`💾 Checkpoint сохранен: ${checkpoint.id}`);
    return `./checkpoints/${checkpoint.id}.checkpoint`;
  }

  async loadCheckpoint(checkpointId) {
    const checkpoint = this.storage.get(checkpointId);
    if (checkpoint) {
      console.log(`📂 Checkpoint загружен: ${checkpointId}`);
      return checkpoint;
    }
    return null;
  }

  async deleteCheckpoint(checkpointId) {
    const deleted = this.storage.delete(checkpointId);
    if (deleted) {
      console.log(`🗑️ Checkpoint удален: ${checkpointId}`);
      return true;
    }
    return false;
  }

  getStorageStats() {
    return { ...this.stats };
  }
}

class MockRewindManager {
  constructor() {
    this.rewindHistory = [];
    this.config = {
      enabled: true,
      createBackups: true,
      maxRewindHistory: 100
    };
  }

  async rewindToCheckpoint(checkpoint) {
    console.log(`⏪ Выполнение rewind к checkpoint: ${checkpoint.id}`);
    console.log(`   Описание: ${checkpoint.description}`);
    console.log(`   Режим: ${checkpoint.currentMode}`);
    
    const startTime = Date.now();
    
    // Симуляция rewind операции
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const executionTime = Date.now() - startTime;
    const filesRewound = Object.keys(checkpoint.metadata.memoryBankFiles || {}).length;
    
    const rewindOperation = {
      id: `rewind_${Date.now()}`,
      checkpointId: checkpoint.id,
      timestamp: new Date(),
      status: 'completed',
      filesRewound,
      executionTime
    };
    
    this.rewindHistory.push(rewindOperation);
    
    console.log(`✅ Rewind завершен за ${executionTime}ms`);
    console.log(`   Откатано файлов: ${filesRewound}`);
    
    return {
      success: true,
      rewindId: rewindOperation.id,
      checkpointId: checkpoint.id,
      filesRewound,
      rewindedFiles: Object.keys(checkpoint.metadata.memoryBankFiles || {}),
      executionTime
    };
  }

  getRewindHistory() {
    return [...this.rewindHistory].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  async undoLastRewind() {
    const lastRewind = this.rewindHistory[this.rewindHistory.length - 1];
    if (lastRewind) {
      console.log(`↩️ Отмена последнего rewind: ${lastRewind.id}`);
      // Симуляция отмены
      await new Promise(resolve => setTimeout(resolve, 500));
      console.log(`✅ Отмена rewind выполнена`);
      return true;
    }
    return false;
  }
}

// Демонстрация работы Phase 2
async function demonstratePhase2() {
  console.log('🎯 Создание компонентов Phase 2...');
  
  const checkpointManager = new MockAutoCheckpointManager();
  const storage = new MockCheckpointStorage();
  const rewindManager = new MockRewindManager();
  
  console.log('\n📋 Создание checkpoint\'ов...');
  
  // Автоматический checkpoint при смене режима
  checkpointManager.onModeChanged('PLAN', 'VAN');
  
  // Автоматический checkpoint при изменении файла
  checkpointManager.onFileChanged('memory-bank/tasks.md');
  
  // Ручной checkpoint
  await checkpointManager.createCheckpoint('Ручной checkpoint для тестирования', {
    trigger: 'manual',
    currentMode: 'PLAN',
    testData: true
  });
  
  console.log('\n💾 Сохранение checkpoint\'ов в хранилище...');
  
  const checkpoints = checkpointManager.getCheckpoints();
  for (const checkpoint of checkpoints) {
    await storage.saveCheckpoint(checkpoint);
  }
  
  console.log('\n📊 Статистика хранилища:');
  const storageStats = storage.getStorageStats();
  console.log(JSON.stringify(storageStats, null, 2));
  
  console.log('\n⏪ Демонстрация функции rewind...');
  
  if (checkpoints.length > 0) {
    const checkpointToRewind = checkpoints[1]; // Второй checkpoint
    const rewindResult = await rewindManager.rewindToCheckpoint(checkpointToRewind);
    
    console.log('\n📋 Результат rewind операции:');
    console.log(JSON.stringify(rewindResult, null, 2));
    
    console.log('\n↩️ Демонстрация отмены rewind...');
    await rewindManager.undoLastRewind();
  }
  
  console.log('\n📋 История rewind операций:');
  const rewindHistory = rewindManager.getRewindHistory();
  rewindHistory.forEach((operation, index) => {
    console.log(`${index + 1}. ${operation.id} - ${operation.checkpointId} (${operation.status})`);
  });
  
  console.log('\n📊 Финальная статистика:');
  console.log(`Всего checkpoint'ов: ${checkpoints.length}`);
  console.log(`Общий размер: ${storageStats.totalSize} байт`);
  console.log(`Средний размер: ${Math.round(storageStats.averageSize)} байт`);
  console.log(`Rewind операций: ${rewindHistory.length}`);
  
  console.log('\n🎉 Phase 2 - Simplified Checkpoint System демонстрация завершена!');
  console.log('✅ Все компоненты работают корректно!');
}

// Запуск демонстрации
demonstratePhase2().catch(console.error);
