/**
 * RewindManager - Класс для отката изменений (rewind functionality)
 */

import * as fs from 'fs';
import * as path from 'path';
import { CheckpointInfo } from '../types/RewindTypes';

export interface RewindConfig {
  /** Включить функцию rewind */
  enabled: boolean;
  /** Максимальное количество операций rewind в истории */
  maxRewindHistory: number;
  /** Включить автоматическое создание backup'ов перед rewind */
  createBackups: boolean;
  /** Директория для backup'ов */
  backupDirectory: string;
  /** Включить детальное логирование */
  verboseLogging: boolean;
}

export interface RewindOperation {
  /** ID операции rewind */
  id: string;
  /** ID checkpoint'а для отката */
  checkpointId: string;
  /** Время выполнения операции */
  timestamp: Date;
  /** Статус операции */
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  /** Количество откатанных файлов */
  filesRewound: number;
  /** Сообщение об ошибке */
  error?: string;
  /** Метаданные операции */
  metadata: Record<string, any>;
}

export interface RewindResult {
  /** Успешность операции */
  success: boolean;
  /** ID операции rewind */
  rewindId: string;
  /** ID checkpoint'а */
  checkpointId: string;
  /** Количество откатанных файлов */
  filesRewound: number;
  /** Список откатанных файлов */
  rewindedFiles: string[];
  /** Время выполнения операции */
  executionTime: number;
  /** Сообщение об ошибке */
  error?: string;
}

export class RewindManager {
  private config: RewindConfig;
  private rewindHistory: RewindOperation[] = [];

  constructor(config?: Partial<RewindConfig>) {
    this.config = {
      enabled: true,
      maxRewindHistory: 100,
      createBackups: true,
      backupDirectory: './backups',
      verboseLogging: false,
      ...config
    };

    this.initializeBackupDirectory();
    this.log('RewindManager initialized', { config: this.config });
  }

  /**
   * Выполнение rewind к checkpoint'у
   */
  async rewindToCheckpoint(checkpoint: CheckpointInfo): Promise<RewindResult> {
    if (!this.config.enabled) {
      throw new Error('Rewind functionality is disabled');
    }

    const startTime = Date.now();
    const rewindId = this.generateRewindId();
    
    // Создание операции rewind
    const rewindOperation: RewindOperation = {
      id: rewindId,
      checkpointId: checkpoint.id,
      timestamp: new Date(),
      status: 'pending',
      filesRewound: 0,
      metadata: {
        checkpointDescription: checkpoint.description,
        checkpointMode: checkpoint.currentMode,
        changedFilesCount: checkpoint.changedFiles.length
      }
    };

    this.rewindHistory.push(rewindOperation);
    rewindOperation.status = 'in_progress';

    try {
      this.log(`Starting rewind to checkpoint: ${checkpoint.id}`, {
        description: checkpoint.description,
        changedFiles: checkpoint.changedFiles.length
      });

      // Создание backup'а текущего состояния (если включено)
      if (this.config.createBackups) {
        await this.createBackup(checkpoint.id);
      }

      // Выполнение rewind
      const rewindedFiles = await this.performRewind(checkpoint);
      
      // Обновление операции
      rewindOperation.status = 'completed';
      rewindOperation.filesRewound = rewindedFiles.length;

      const executionTime = Date.now() - startTime;

      const result: RewindResult = {
        success: true,
        rewindId,
        checkpointId: checkpoint.id,
        filesRewound: rewindedFiles.length,
        rewindedFiles,
        executionTime
      };

      this.log(`Rewind completed successfully: ${checkpoint.id}`, {
        rewindId,
        filesRewound: rewindedFiles.length,
        executionTime
      });

      // Очистка истории rewind'ов
      this.cleanupRewindHistory();

      return result;

    } catch (error) {
      rewindOperation.status = 'failed';
      rewindOperation.error = error instanceof Error ? error.message : String(error);

      const executionTime = Date.now() - startTime;

      const result: RewindResult = {
        success: false,
        rewindId,
        checkpointId: checkpoint.id,
        filesRewound: 0,
        rewindedFiles: [],
        executionTime,
        error: rewindOperation.error
      };

      this.log(`Rewind failed: ${checkpoint.id}`, {
        rewindId,
        error: rewindOperation.error,
        executionTime
      });

      throw error;
    }
  }

  /**
   * Получение истории rewind операций
   */
  getRewindHistory(): RewindOperation[] {
    return [...this.rewindHistory].sort((a, b) => 
      b.timestamp.getTime() - a.timestamp.getTime()
    );
  }

  /**
   * Получение последней операции rewind
   */
  getLastRewindOperation(): RewindOperation | null {
    const sortedHistory = this.getRewindHistory();
    return sortedHistory.length > 0 ? sortedHistory[0] : null;
  }

  /**
   * Отмена последней операции rewind (если возможно)
   */
  async undoLastRewind(): Promise<boolean> {
    try {
      const lastOperation = this.getLastRewindOperation();
      if (!lastOperation || lastOperation.status !== 'completed') {
        this.log('No completed rewind operation to undo');
        return false;
      }

      // Восстановление из backup'а
      if (this.config.createBackups) {
        const backupRestored = await this.restoreFromBackup(lastOperation.checkpointId);
        if (backupRestored) {
          this.log(`Undo rewind completed: ${lastOperation.id}`);
          return true;
        }
      }

      this.log(`Cannot undo rewind: ${lastOperation.id} (no backup available)`);
      return false;

    } catch (error) {
      this.log(`Failed to undo last rewind`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Выполнение rewind операции
   */
  private async performRewind(checkpoint: CheckpointInfo): Promise<string[]> {
    const rewindedFiles: string[] = [];

    try {
      // Получение файлов из checkpoint'а
      const checkpointFiles = checkpoint.metadata.memoryBankFiles || {};
      
      for (const [filePath, fileInfo] of Object.entries(checkpointFiles)) {
        if (fileInfo.exists) {
          // В реальной реализации здесь будет восстановление содержимого файла
          // из checkpoint'а. Для демонстрации просто логируем операцию
          
          this.log(`Rewinding file: ${filePath}`, {
            size: fileInfo.size,
            modified: fileInfo.modified
          });
          
          rewindedFiles.push(filePath);
        } else {
          // Файл был удален в checkpoint'е, удаляем его
          if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            this.log(`Deleted file during rewind: ${filePath}`);
            rewindedFiles.push(filePath);
          }
        }
      }

      // Восстановление режима Memory Bank
      if (checkpoint.currentMode) {
        this.log(`Restoring Memory Bank mode: ${checkpoint.currentMode}`);
        // Здесь будет логика восстановления режима
      }

      return rewindedFiles;

    } catch (error) {
      this.log(`Error during rewind operation`, {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Создание backup'а текущего состояния
   */
  private async createBackup(checkpointId: string): Promise<void> {
    try {
      const backupId = `backup_${checkpointId}_${Date.now()}`;
      const backupPath = path.join(this.config.backupDirectory, `${backupId}.json`);
      
      // Создание backup'а текущих Memory Bank файлов
      const backupData = {
        id: backupId,
        checkpointId,
        timestamp: new Date().toISOString(),
        files: {}
      };

      const memoryBankFiles = [
        'memory-bank/tasks.md',
        'memory-bank/activeContext.md',
        'memory-bank/progress.md',
        'memory-bank/projectbrief.md',
        'memory-bank/productContext.md',
        'memory-bank/systemPatterns.md',
        'memory-bank/techContext.md'
      ];

      for (const filePath of memoryBankFiles) {
        if (fs.existsSync(filePath)) {
          try {
            const content = fs.readFileSync(filePath, 'utf8');
            const stats = fs.statSync(filePath);
            backupData.files[filePath] = {
              content,
              size: stats.size,
              modified: stats.mtime.toISOString()
            };
          } catch (error) {
            this.log(`Failed to backup file: ${filePath}`, {
              error: error instanceof Error ? error.message : String(error)
            });
          }
        }
      }

      // Сохранение backup'а
      fs.writeFileSync(backupPath, JSON.stringify(backupData, null, 2), 'utf8');
      
      this.log(`Backup created: ${backupId}`, {
        backupPath,
        filesCount: Object.keys(backupData.files).length
      });

    } catch (error) {
      this.log(`Failed to create backup for checkpoint: ${checkpointId}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Восстановление из backup'а
   */
  private async restoreFromBackup(checkpointId: string): Promise<boolean> {
    try {
      // Поиск backup'а для данного checkpoint'а
      const backupFiles = fs.readdirSync(this.config.backupDirectory)
        .filter(file => file.includes(checkpointId) && file.endsWith('.json'));
      
      if (backupFiles.length === 0) {
        this.log(`No backup found for checkpoint: ${checkpointId}`);
        return false;
      }

      // Использование последнего backup'а
      const latestBackup = backupFiles.sort().pop()!;
      const backupPath = path.join(this.config.backupDirectory, latestBackup);
      
      // Загрузка backup'а
      const backupData = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
      
      // Восстановление файлов
      for (const [filePath, fileInfo] of Object.entries(backupData.files)) {
        if (fileInfo && typeof fileInfo === 'object' && 'content' in fileInfo) {
          fs.writeFileSync(filePath, fileInfo.content, 'utf8');
          this.log(`Restored file from backup: ${filePath}`);
        }
      }

      this.log(`Restored from backup: ${latestBackup}`, {
        filesCount: Object.keys(backupData.files).length
      });

      return true;

    } catch (error) {
      this.log(`Failed to restore from backup for checkpoint: ${checkpointId}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Инициализация директории backup'ов
   */
  private initializeBackupDirectory(): void {
    if (!fs.existsSync(this.config.backupDirectory)) {
      fs.mkdirSync(this.config.backupDirectory, { recursive: true });
      this.log(`Backup directory created: ${this.config.backupDirectory}`);
    }
  }

  /**
   * Очистка истории rewind операций
   */
  private cleanupRewindHistory(): void {
    if (this.rewindHistory.length > this.config.maxRewindHistory) {
      const sortedHistory = this.rewindHistory.sort((a, b) => 
        a.timestamp.getTime() - b.timestamp.getTime()
      );
      
      const operationsToRemove = sortedHistory.slice(
        0, 
        this.rewindHistory.length - this.config.maxRewindHistory
      );
      
      for (const operation of operationsToRemove) {
        const index = this.rewindHistory.findIndex(op => op.id === operation.id);
        if (index !== -1) {
          this.rewindHistory.splice(index, 1);
        }
      }
      
      this.log(`Cleaned up rewind history: ${operationsToRemove.length} operations removed`);
    }
  }

  /**
   * Генерация уникального ID операции rewind
   */
  private generateRewindId(): string {
    return `rewind_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<RewindConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[RewindManager] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    this.rewindHistory = [];
    this.log('RewindManager destroyed');
  }
}
