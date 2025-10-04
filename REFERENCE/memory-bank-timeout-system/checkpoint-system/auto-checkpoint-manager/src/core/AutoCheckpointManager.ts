/**
 * AutoCheckpointManager - Класс для автоматического создания checkpoint'ов
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { 
  CheckpointInfo, 
  AutoCheckpointConfig, 
  AutoCheckpointStats, 
  FileChangeInfo 
} from '../types/CheckpointTypes';

export class AutoCheckpointManager extends EventEmitter {
  private config: AutoCheckpointConfig;
  private checkpoints: Map<string, CheckpointInfo> = new Map();
  private stats: AutoCheckpointStats;
  private intervalTimer: NodeJS.Timeout | null = null;
  private isWatching: boolean = false;

  constructor(config?: Partial<AutoCheckpointConfig>) {
    super();
    
    this.config = {
      enabled: true,
      interval: 300000, // 5 минут
      maxCheckpoints: 50,
      onFileChange: true,
      onModeChange: true,
      onCommandExecution: true,
      verboseLogging: false,
      checkpointDirectory: './checkpoints',
      monitoredFiles: [
        'memory-bank/tasks.md',
        'memory-bank/activeContext.md',
        'memory-bank/progress.md',
        'memory-bank/projectbrief.md',
        'memory-bank/productContext.md',
        'memory-bank/systemPatterns.md',
        'memory-bank/techContext.md'
      ],
      excludedFiles: [
        '*.tmp',
        '*.log',
        'node_modules/**',
        '.git/**'
      ],
      ...config
    };

    this.stats = {
      totalCheckpoints: 0,
      activeCheckpoints: 0,
      deletedCheckpoints: 0,
      totalSize: 0,
      averageSize: 0,
      lastCheckpointTime: null,
      lastUpdated: new Date()
    };

    this.initializeCheckpointDirectory();
    this.startAutoCheckpoints();
    
    this.log('AutoCheckpointManager initialized', { config: this.config });
  }

  /**
   * Создание checkpoint'а
   */
  async createCheckpoint(
    description: string,
    metadata?: Record<string, any>
  ): Promise<string> {
    if (!this.config.enabled) {
      this.log('Checkpoint creation disabled', { description });
      return '';
    }

    try {
      const checkpointId = this.generateCheckpointId();
      const timestamp = new Date();
      
      // Получение измененных файлов
      const changedFiles = await this.getChangedFiles();
      
      // Создание метаданных
      const checkpointMetadata = {
        description,
        currentMode: metadata?.currentMode || 'UNKNOWN',
        changedFilesCount: changedFiles.length,
        memoryBankFiles: this.getMemoryBankFiles(),
        ...metadata
      };

      // Создание информации о checkpoint'е
      const checkpoint: CheckpointInfo = {
        id: checkpointId,
        timestamp,
        description,
        currentMode: checkpointMetadata.currentMode,
        changedFiles,
        metadata: checkpointMetadata,
        size: 0, // Будет вычислен при сохранении
        filePath: path.join(this.config.checkpointDirectory, `${checkpointId}.json`)
      };

      // Сохранение checkpoint'а
      await this.saveCheckpoint(checkpoint);
      
      // Добавление в список
      this.checkpoints.set(checkpointId, checkpoint);
      
      // Обновление статистики
      this.updateStats(checkpoint);
      
      // Очистка старых checkpoint'ов
      this.cleanupOldCheckpoints();
      
      this.log(`Checkpoint created: ${description}`, {
        checkpointId,
        changedFiles: changedFiles.length,
        size: checkpoint.size
      });
      
      this.emit('checkpointCreated', checkpoint);
      return checkpointId;
      
    } catch (error) {
      this.log(`Failed to create checkpoint: ${description}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      
      this.emit('checkpointError', error instanceof Error ? error : new Error(String(error)));
      throw error;
    }
  }

  /**
   * Удаление checkpoint'а
   */
  async deleteCheckpoint(checkpointId: string): Promise<boolean> {
    try {
      const checkpoint = this.checkpoints.get(checkpointId);
      if (!checkpoint) {
        return false;
      }

      // Удаление файла checkpoint'а
      if (fs.existsSync(checkpoint.filePath)) {
        fs.unlinkSync(checkpoint.filePath);
      }

      // Удаление из списка
      this.checkpoints.delete(checkpointId);
      
      // Обновление статистики
      this.stats.deletedCheckpoints++;
      this.stats.activeCheckpoints--;
      this.stats.totalSize -= checkpoint.size;
      this.stats.averageSize = this.stats.totalSize / this.stats.activeCheckpoints;
      this.stats.lastUpdated = new Date();
      
      this.log(`Checkpoint deleted: ${checkpointId}`, {
        description: checkpoint.description
      });
      
      this.emit('checkpointDeleted', checkpointId);
      return true;
      
    } catch (error) {
      this.log(`Failed to delete checkpoint: ${checkpointId}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Получение списка checkpoint'ов
   */
  getCheckpoints(): CheckpointInfo[] {
    return Array.from(this.checkpoints.values()).sort((a, b) => 
      b.timestamp.getTime() - a.timestamp.getTime()
    );
  }

  /**
   * Получение checkpoint'а по ID
   */
  getCheckpoint(checkpointId: string): CheckpointInfo | undefined {
    return this.checkpoints.get(checkpointId);
  }

  /**
   * Получение статистики
   */
  getStats(): AutoCheckpointStats {
    return { ...this.stats };
  }

  /**
   * Обработка изменения файла
   */
  onFileChanged(filePath: string): void {
    if (!this.config.onFileChange) return;
    
    // Проверка, нужно ли отслеживать этот файл
    if (!this.shouldMonitorFile(filePath)) return;
    
    this.log(`File changed: ${filePath}`);
    this.emit('fileChanged', filePath);
    
    // Создание checkpoint'а при изменении важных файлов
    if (this.isMemoryBankFile(filePath)) {
      this.createCheckpoint(
        `Автоматический checkpoint: файл ${path.basename(filePath)} изменен`,
        { trigger: 'fileChange', filePath }
      ).catch(error => {
        this.log(`Failed to create auto checkpoint for file change: ${filePath}`, {
          error: error instanceof Error ? error.message : String(error)
        });
      });
    }
  }

  /**
   * Обработка смены режима
   */
  onModeChanged(newMode: string, previousMode: string): void {
    if (!this.config.onModeChange) return;
    
    this.log(`Mode changed: ${previousMode} → ${newMode}`);
    this.emit('modeChanged', newMode, previousMode);
    
    // Создание checkpoint'а при смене режима
    this.createCheckpoint(
      `Переход из режима ${previousMode} в режим ${newMode}`,
      { trigger: 'modeChange', previousMode, newMode }
    ).catch(error => {
      this.log(`Failed to create auto checkpoint for mode change: ${previousMode} → ${newMode}`, {
        error: error instanceof Error ? error.message : String(error)
      });
    });
  }

  /**
   * Обработка выполнения команды
   */
  onCommandExecuted(command: string, result: any): void {
    if (!this.config.onCommandExecution) return;
    
    this.log(`Command executed: ${command}`);
    this.emit('commandExecuted', command, result);
    
    // Создание checkpoint'а при выполнении важных команд
    if (this.isImportantCommand(command)) {
      this.createCheckpoint(
        `Команда выполнена: ${command}`,
        { trigger: 'commandExecution', command, success: result.success }
      ).catch(error => {
        this.log(`Failed to create auto checkpoint for command: ${command}`, {
          error: error instanceof Error ? error.message : String(error)
        });
      });
    }
  }

  /**
   * Инициализация директории checkpoint'ов
   */
  private initializeCheckpointDirectory(): void {
    if (!fs.existsSync(this.config.checkpointDirectory)) {
      fs.mkdirSync(this.config.checkpointDirectory, { recursive: true });
      this.log(`Checkpoint directory created: ${this.config.checkpointDirectory}`);
    }
  }

  /**
   * Запуск автоматических checkpoint'ов
   */
  private startAutoCheckpoints(): void {
    if (!this.config.enabled || this.config.interval <= 0) return;
    
    this.intervalTimer = setInterval(() => {
      this.createCheckpoint(
        'Автоматический checkpoint по расписанию',
        { trigger: 'scheduled' }
      ).catch(error => {
        this.log('Failed to create scheduled checkpoint', {
          error: error instanceof Error ? error.message : String(error)
        });
      });
    }, this.config.interval);
    
    this.log(`Auto checkpoints started with interval: ${this.config.interval}ms`);
  }

  /**
   * Остановка автоматических checkpoint'ов
   */
  stopAutoCheckpoints(): void {
    if (this.intervalTimer) {
      clearInterval(this.intervalTimer);
      this.intervalTimer = null;
    }
    
    this.log('Auto checkpoints stopped');
  }

  /**
   * Получение измененных файлов
   */
  private async getChangedFiles(): Promise<string[]> {
    const changedFiles: string[] = [];
    
    for (const filePath of this.config.monitoredFiles) {
      if (fs.existsSync(filePath)) {
        changedFiles.push(filePath);
      }
    }
    
    return changedFiles;
  }

  /**
   * Получение Memory Bank файлов
   */
  private getMemoryBankFiles(): Record<string, any> {
    const files: Record<string, any> = {};
    
    for (const filePath of this.config.monitoredFiles) {
      if (fs.existsSync(filePath)) {
        try {
          const stats = fs.statSync(filePath);
          files[filePath] = {
            size: stats.size,
            modified: stats.mtime,
            exists: true
          };
        } catch (error) {
          files[filePath] = {
            exists: false,
            error: error instanceof Error ? error.message : String(error)
          };
        }
      }
    }
    
    return files;
  }

  /**
   * Сохранение checkpoint'а
   */
  private async saveCheckpoint(checkpoint: CheckpointInfo): Promise<void> {
    const checkpointData = {
      ...checkpoint,
      timestamp: checkpoint.timestamp.toISOString()
    };
    
    const data = JSON.stringify(checkpointData, null, 2);
    fs.writeFileSync(checkpoint.filePath, data, 'utf8');
    
    // Обновление размера
    checkpoint.size = Buffer.byteLength(data, 'utf8');
  }

  /**
   * Очистка старых checkpoint'ов
   */
  private cleanupOldCheckpoints(): void {
    if (this.checkpoints.size <= this.config.maxCheckpoints) return;
    
    const sortedCheckpoints = Array.from(this.checkpoints.values())
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    
    const checkpointsToDelete = sortedCheckpoints.slice(
      0, 
      this.checkpoints.size - this.config.maxCheckpoints
    );
    
    for (const checkpoint of checkpointsToDelete) {
      this.deleteCheckpoint(checkpoint.id);
    }
  }

  /**
   * Проверка, нужно ли отслеживать файл
   */
  private shouldMonitorFile(filePath: string): boolean {
    // Проверка исключений
    for (const pattern of this.config.excludedFiles) {
      if (this.matchesPattern(filePath, pattern)) {
        return false;
      }
    }
    
    return true;
  }

  /**
   * Проверка, является ли файл Memory Bank файлом
   */
  private isMemoryBankFile(filePath: string): boolean {
    return this.config.monitoredFiles.some(monitoredFile => 
      filePath.includes(monitoredFile)
    );
  }

  /**
   * Проверка, является ли команда важной
   */
  private isImportantCommand(command: string): boolean {
    const importantCommands = ['npm', 'git', 'tsc', 'build', 'test'];
    return importantCommands.some(important => command.includes(important));
  }

  /**
   * Проверка соответствия паттерну
   */
  private matchesPattern(filePath: string, pattern: string): boolean {
    // Простая проверка паттерна (в реальной реализации можно использовать minimatch)
    return filePath.includes(pattern.replace('*', ''));
  }

  /**
   * Обновление статистики
   */
  private updateStats(checkpoint: CheckpointInfo): void {
    this.stats.totalCheckpoints++;
    this.stats.activeCheckpoints++;
    this.stats.totalSize += checkpoint.size;
    this.stats.averageSize = this.stats.totalSize / this.stats.activeCheckpoints;
    this.stats.lastCheckpointTime = checkpoint.timestamp;
    this.stats.lastUpdated = new Date();
  }

  /**
   * Генерация уникального ID checkpoint'а
   */
  private generateCheckpointId(): string {
    return `checkpoint_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<AutoCheckpointConfig>): void {
    this.config = { ...this.config, ...config };
    
    // Перезапуск автоматических checkpoint'ов если изменился интервал
    if (this.intervalTimer) {
      this.stopAutoCheckpoints();
      this.startAutoCheckpoints();
    }
    
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[AutoCheckpointManager] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    this.stopAutoCheckpoints();
    this.checkpoints.clear();
    this.removeAllListeners();
    
    this.log('AutoCheckpointManager destroyed');
  }
}
