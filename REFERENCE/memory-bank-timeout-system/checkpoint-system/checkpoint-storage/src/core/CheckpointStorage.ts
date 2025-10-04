/**
 * CheckpointStorage - Класс для хранения и управления checkpoint'ами
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { CheckpointInfo } from '../types/StorageTypes';

export interface StorageConfig {
  /** Путь к директории хранения checkpoint'ов */
  storageDirectory: string;
  /** Максимальный размер одного checkpoint'а (байты) */
  maxCheckpointSize: number;
  /** Максимальное количество checkpoint'ов */
  maxCheckpoints: number;
  /** Включить сжатие checkpoint'ов */
  enableCompression: boolean;
  /** Включить шифрование checkpoint'ов */
  enableEncryption: boolean;
  /** Ключ шифрования */
  encryptionKey?: string;
  /** Включить детальное логирование */
  verboseLogging: boolean;
}

export interface StorageStats {
  /** Общее количество checkpoint'ов */
  totalCheckpoints: number;
  /** Общий размер в байтах */
  totalSize: number;
  /** Средний размер checkpoint'а */
  averageSize: number;
  /** Размер сжатых данных */
  compressedSize: number;
  /** Коэффициент сжатия */
  compressionRatio: number;
  /** Время последнего обновления */
  lastUpdated: Date;
}

export class CheckpointStorage {
  private config: StorageConfig;
  private stats: StorageStats;

  constructor(config?: Partial<StorageConfig>) {
    this.config = {
      storageDirectory: './checkpoints',
      maxCheckpointSize: 10 * 1024 * 1024, // 10 MB
      maxCheckpoints: 100,
      enableCompression: true,
      enableEncryption: false,
      verboseLogging: false,
      ...config
    };

    this.stats = {
      totalCheckpoints: 0,
      totalSize: 0,
      averageSize: 0,
      compressedSize: 0,
      compressionRatio: 1,
      lastUpdated: new Date()
    };

    this.initializeStorage();
    this.log('CheckpointStorage initialized', { config: this.config });
  }

  /**
   * Сохранение checkpoint'а
   */
  async saveCheckpoint(checkpoint: CheckpointInfo): Promise<string> {
    try {
      // Валидация checkpoint'а
      this.validateCheckpoint(checkpoint);
      
      // Подготовка данных для сохранения
      const checkpointData = {
        ...checkpoint,
        timestamp: checkpoint.timestamp.toISOString(),
        savedAt: new Date().toISOString()
      };
      
      let data = JSON.stringify(checkpointData, null, 2);
      const originalSize = Buffer.byteLength(data, 'utf8');
      
      // Проверка размера
      if (originalSize > this.config.maxCheckpointSize) {
        throw new Error(`Checkpoint too large: ${originalSize} bytes (max: ${this.config.maxCheckpointSize})`);
      }
      
      // Сжатие (если включено)
      if (this.config.enableCompression) {
        data = await this.compressData(data);
      }
      
      // Шифрование (если включено)
      if (this.config.enableEncryption && this.config.encryptionKey) {
        data = this.encryptData(data, this.config.encryptionKey);
      }
      
      // Определение пути к файлу
      const fileName = `${checkpoint.id}.checkpoint`;
      const filePath = path.join(this.config.storageDirectory, fileName);
      
      // Сохранение в файл
      fs.writeFileSync(filePath, data, 'utf8');
      
      // Обновление статистики
      this.updateStats(originalSize, Buffer.byteLength(data, 'utf8'));
      
      this.log(`Checkpoint saved: ${checkpoint.id}`, {
        originalSize,
        compressedSize: Buffer.byteLength(data, 'utf8'),
        filePath
      });
      
      return filePath;
      
    } catch (error) {
      this.log(`Failed to save checkpoint: ${checkpoint.id}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Загрузка checkpoint'а
   */
  async loadCheckpoint(checkpointId: string): Promise<CheckpointInfo | null> {
    try {
      const fileName = `${checkpointId}.checkpoint`;
      const filePath = path.join(this.config.storageDirectory, fileName);
      
      if (!fs.existsSync(filePath)) {
        this.log(`Checkpoint not found: ${checkpointId}`, { filePath });
        return null;
      }
      
      // Чтение файла
      let data = fs.readFileSync(filePath, 'utf8');
      
      // Расшифровка (если включено)
      if (this.config.enableEncryption && this.config.encryptionKey) {
        data = this.decryptData(data, this.config.encryptionKey);
      }
      
      // Распаковка (если включено)
      if (this.config.enableCompression) {
        data = await this.decompressData(data);
      }
      
      // Парсинг JSON
      const checkpointData = JSON.parse(data);
      
      // Восстановление типов
      checkpointData.timestamp = new Date(checkpointData.timestamp);
      
      this.log(`Checkpoint loaded: ${checkpointId}`, {
        filePath,
        size: Buffer.byteLength(data, 'utf8')
      });
      
      return checkpointData as CheckpointInfo;
      
    } catch (error) {
      this.log(`Failed to load checkpoint: ${checkpointId}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return null;
    }
  }

  /**
   * Удаление checkpoint'а
   */
  async deleteCheckpoint(checkpointId: string): Promise<boolean> {
    try {
      const fileName = `${checkpointId}.checkpoint`;
      const filePath = path.join(this.config.storageDirectory, fileName);
      
      if (!fs.existsSync(filePath)) {
        this.log(`Checkpoint not found for deletion: ${checkpointId}`, { filePath });
        return false;
      }
      
      // Получение размера файла для статистики
      const stats = fs.statSync(filePath);
      
      // Удаление файла
      fs.unlinkSync(filePath);
      
      // Обновление статистики
      this.stats.totalCheckpoints--;
      this.stats.totalSize -= stats.size;
      this.stats.averageSize = this.stats.totalCheckpoints > 0 ? 
        this.stats.totalSize / this.stats.totalCheckpoints : 0;
      this.stats.lastUpdated = new Date();
      
      this.log(`Checkpoint deleted: ${checkpointId}`, {
        filePath,
        size: stats.size
      });
      
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
  getCheckpointList(): string[] {
    try {
      if (!fs.existsSync(this.config.storageDirectory)) {
        return [];
      }
      
      const files = fs.readdirSync(this.config.storageDirectory);
      const checkpoints = files
        .filter(file => file.endsWith('.checkpoint'))
        .map(file => file.replace('.checkpoint', ''))
        .sort();
      
      this.log(`Found ${checkpoints.length} checkpoints`, { checkpoints });
      return checkpoints;
      
    } catch (error) {
      this.log(`Failed to get checkpoint list`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return [];
    }
  }

  /**
   * Получение статистики хранилища
   */
  getStorageStats(): StorageStats {
    this.refreshStats();
    return { ...this.stats };
  }

  /**
   * Очистка старых checkpoint'ов
   */
  async cleanupOldCheckpoints(): Promise<number> {
    try {
      const checkpoints = this.getCheckpointList();
      
      if (checkpoints.length <= this.config.maxCheckpoints) {
        return 0;
      }
      
      // Получение информации о checkpoint'ах
      const checkpointInfos = [];
      for (const checkpointId of checkpoints) {
        const checkpoint = await this.loadCheckpoint(checkpointId);
        if (checkpoint) {
          checkpointInfos.push(checkpoint);
        }
      }
      
      // Сортировка по времени (старые сначала)
      checkpointInfos.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      
      // Удаление старых checkpoint'ов
      const checkpointsToDelete = checkpointInfos.slice(
        0, 
        checkpointInfos.length - this.config.maxCheckpoints
      );
      
      let deletedCount = 0;
      for (const checkpoint of checkpointsToDelete) {
        if (await this.deleteCheckpoint(checkpoint.id)) {
          deletedCount++;
        }
      }
      
      this.log(`Cleanup completed: ${deletedCount} checkpoints deleted`);
      return deletedCount;
      
    } catch (error) {
      this.log(`Failed to cleanup old checkpoints`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return 0;
    }
  }

  /**
   * Инициализация хранилища
   */
  private initializeStorage(): void {
    if (!fs.existsSync(this.config.storageDirectory)) {
      fs.mkdirSync(this.config.storageDirectory, { recursive: true });
      this.log(`Storage directory created: ${this.config.storageDirectory}`);
    }
    
    // Обновление статистики
    this.refreshStats();
  }

  /**
   * Валидация checkpoint'а
   */
  private validateCheckpoint(checkpoint: CheckpointInfo): void {
    if (!checkpoint.id || typeof checkpoint.id !== 'string') {
      throw new Error('Invalid checkpoint ID');
    }
    
    if (!checkpoint.timestamp || !(checkpoint.timestamp instanceof Date)) {
      throw new Error('Invalid checkpoint timestamp');
    }
    
    if (!checkpoint.description || typeof checkpoint.description !== 'string') {
      throw new Error('Invalid checkpoint description');
    }
  }

  /**
   * Сжатие данных
   */
  private async compressData(data: string): Promise<string> {
    // В реальной реализации здесь будет использоваться zlib или другая библиотека сжатия
    // Для демонстрации просто возвращаем исходные данные
    return data;
  }

  /**
   * Распаковка данных
   */
  private async decompressData(data: string): Promise<string> {
    // В реальной реализации здесь будет распаковка
    return data;
  }

  /**
   * Шифрование данных
   */
  private encryptData(data: string, key: string): string {
    if (!key) return data;
    
    // Простое шифрование для демонстрации
    const cipher = crypto.createCipher('aes-256-cbc', key);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }

  /**
   * Расшифровка данных
   */
  private decryptData(data: string, key: string): string {
    if (!key) return data;
    
    // Простая расшифровка для демонстрации
    const decipher = crypto.createDecipher('aes-256-cbc', key);
    let decrypted = decipher.update(data, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }

  /**
   * Обновление статистики
   */
  private updateStats(originalSize: number, compressedSize: number): void {
    this.stats.totalCheckpoints++;
    this.stats.totalSize += originalSize;
    this.stats.compressedSize += compressedSize;
    this.stats.averageSize = this.stats.totalSize / this.stats.totalCheckpoints;
    this.stats.compressionRatio = this.stats.compressedSize / this.stats.totalSize;
    this.stats.lastUpdated = new Date();
  }

  /**
   * Обновление статистики из файловой системы
   */
  private refreshStats(): void {
    try {
      const checkpoints = this.getCheckpointList();
      this.stats.totalCheckpoints = checkpoints.length;
      
      let totalSize = 0;
      for (const checkpointId of checkpoints) {
        const fileName = `${checkpointId}.checkpoint`;
        const filePath = path.join(this.config.storageDirectory, fileName);
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          totalSize += stats.size;
        }
      }
      
      this.stats.totalSize = totalSize;
      this.stats.averageSize = checkpoints.length > 0 ? totalSize / checkpoints.length : 0;
      this.stats.lastUpdated = new Date();
      
    } catch (error) {
      this.log(`Failed to refresh stats`, {
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<StorageConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[CheckpointStorage] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    this.log('CheckpointStorage destroyed');
  }
}
