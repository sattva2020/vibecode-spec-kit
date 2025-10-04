/**
 * Типы данных для Checkpoint Storage
 */

/**
 * Информация о checkpoint'е для хранения
 */
export interface CheckpointInfo {
  /** Уникальный ID checkpoint'а */
  id: string;
  /** Время создания */
  timestamp: Date;
  /** Описание checkpoint'а */
  description: string;
  /** Текущий режим Memory Bank */
  currentMode: string;
  /** Измененные файлы */
  changedFiles: string[];
  /** Метаданные checkpoint'а */
  metadata: Record<string, any>;
  /** Размер checkpoint'а в байтах */
  size: number;
  /** Путь к файлу checkpoint'а */
  filePath: string;
}

/**
 * Конфигурация хранилища
 */
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

/**
 * Статистика хранилища
 */
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

/**
 * Информация о файле checkpoint'а
 */
export interface CheckpointFileInfo {
  /** ID checkpoint'а */
  id: string;
  /** Путь к файлу */
  filePath: string;
  /** Размер файла */
  size: number;
  /** Время создания файла */
  createdAt: Date;
  /** Время последнего изменения */
  modifiedAt: Date;
  /** Существует ли файл */
  exists: boolean;
}

/**
 * Операции с checkpoint'ами
 */
export enum CheckpointOperation {
  /** Создание checkpoint'а */
  CREATE = 'create',
  /** Загрузка checkpoint'а */
  LOAD = 'load',
  /** Удаление checkpoint'а */
  DELETE = 'delete',
  /** Обновление checkpoint'а */
  UPDATE = 'update',
  /** Список checkpoint'ов */
  LIST = 'list'
}

/**
 * Результат операции с checkpoint'ом
 */
export interface CheckpointOperationResult {
  /** Успешность операции */
  success: boolean;
  /** ID checkpoint'а */
  checkpointId: string;
  /** Операция */
  operation: CheckpointOperation;
  /** Сообщение об ошибке */
  error?: string;
  /** Время выполнения операции */
  executionTime: number;
  /** Размер данных */
  dataSize?: number;
}
