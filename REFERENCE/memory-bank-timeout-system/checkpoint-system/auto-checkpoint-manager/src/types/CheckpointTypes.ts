/**
 * Типы данных для Auto Checkpoint Manager
 */

/**
 * Информация о checkpoint'е
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
 * Конфигурация Auto Checkpoint Manager
 */
export interface AutoCheckpointConfig {
  /** Включить автоматические checkpoint'ы */
  enabled: boolean;
  /** Интервал создания checkpoint'ов (мс) */
  interval: number;
  /** Максимальное количество checkpoint'ов */
  maxCheckpoints: number;
  /** Включить checkpoint'ы при изменении файлов */
  onFileChange: boolean;
  /** Включить checkpoint'ы при смене режима */
  onModeChange: boolean;
  /** Включить checkpoint'ы при выполнении команд */
  onCommandExecution: boolean;
  /** Включить детальное логирование */
  verboseLogging: boolean;
  /** Путь к директории checkpoint'ов */
  checkpointDirectory: string;
  /** Список файлов для мониторинга */
  monitoredFiles: string[];
  /** Исключения (файлы, которые не нужно отслеживать) */
  excludedFiles: string[];
}

/**
 * События Auto Checkpoint Manager
 */
export interface AutoCheckpointEvents {
  /** Checkpoint создан */
  checkpointCreated: (checkpoint: CheckpointInfo) => void;
  /** Checkpoint удален */
  checkpointDeleted: (checkpointId: string) => void;
  /** Файл изменен */
  fileChanged: (filePath: string) => void;
  /** Режим изменен */
  modeChanged: (newMode: string, previousMode: string) => void;
  /** Команда выполнена */
  commandExecuted: (command: string, result: any) => void;
  /** Ошибка в процессе создания checkpoint'а */
  checkpointError: (error: Error) => void;
}

/**
 * Статистика Auto Checkpoint Manager
 */
export interface AutoCheckpointStats {
  /** Общее количество созданных checkpoint'ов */
  totalCheckpoints: number;
  /** Количество активных checkpoint'ов */
  activeCheckpoints: number;
  /** Количество удаленных checkpoint'ов */
  deletedCheckpoints: number;
  /** Общий размер checkpoint'ов в байтах */
  totalSize: number;
  /** Средний размер checkpoint'а в байтах */
  averageSize: number;
  /** Время последнего checkpoint'а */
  lastCheckpointTime: Date | null;
  /** Время последнего обновления статистики */
  lastUpdated: Date;
}

/**
 * Информация об изменении файла
 */
export interface FileChangeInfo {
  /** Путь к файлу */
  filePath: string;
  /** Время изменения */
  timestamp: Date;
  /** Тип изменения */
  changeType: 'created' | 'modified' | 'deleted' | 'renamed';
  /** Размер файла */
  size: number;
  /** Хеш содержимого файла */
  hash: string;
}
