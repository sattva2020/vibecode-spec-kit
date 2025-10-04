/**
 * Типы данных для Session Manager
 */

/**
 * Режимы Memory Bank
 */
export type MemoryBankMode = 'VAN' | 'PLAN' | 'CREATIVE' | 'IMPLEMENT' | 'REFLECT' | 'ARCHIVE';

/**
 * Информация о режиме
 */
export interface ModeInfo {
  /** Режим */
  mode: MemoryBankMode;
  /** Время переключения */
  timestamp: Date;
  /** Продолжительность в режиме (мс) */
  duration: number;
}

/**
 * Информация о checkpoint'е в сессии
 */
export interface SessionCheckpoint {
  /** ID checkpoint'а */
  id: string;
  /** Описание */
  description: string;
  /** Время создания */
  timestamp: Date;
  /** Режим при создании */
  mode: MemoryBankMode;
  /** Метаданные */
  metadata: Record<string, any>;
}

/**
 * Информация о команде в сессии
 */
export interface SessionCommand {
  /** Команда */
  command: string;
  /** Результат выполнения */
  result: any;
  /** Время выполнения (мс) */
  executionTime: number;
  /** Время выполнения */
  timestamp: Date;
  /** Режим при выполнении */
  mode: MemoryBankMode;
}

/**
 * Информация об изменении файла в сессии
 */
export interface SessionFileChange {
  /** Путь к файлу */
  filePath: string;
  /** Тип изменения */
  changeType: 'created' | 'modified' | 'deleted';
  /** Время изменения */
  timestamp: Date;
  /** Режим при изменении */
  mode: MemoryBankMode;
}

/**
 * Информация о сессии
 */
export interface SessionInfo {
  /** Уникальный ID сессии */
  id: string;
  /** Описание сессии */
  description: string;
  /** Время начала */
  startTime: Date;
  /** Время завершения */
  endTime: Date | null;
  /** Продолжительность сессии (мс) */
  duration: number;
  /** Статус сессии */
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  /** Текущий режим Memory Bank */
  currentMode: MemoryBankMode;
  /** История режимов */
  modeHistory: ModeInfo[];
  /** Checkpoint'ы в сессии */
  checkpoints: SessionCheckpoint[];
  /** Команды в сессии */
  commands: SessionCommand[];
  /** Изменения файлов в сессии */
  fileChanges: SessionFileChange[];
  /** Метаданные сессии */
  metadata: Record<string, any>;
}

/**
 * Конфигурация Session Manager
 */
export interface SessionConfig {
  /** Автоматически начинать новую сессию */
  autoStart: boolean;
  /** Автоматически сохранять сессии */
  autoSave: boolean;
  /** Интервал автосохранения (мс) */
  saveInterval: number;
  /** Максимальное количество сессий в истории */
  maxSessions: number;
  /** Директория для сохранения сессий */
  sessionDirectory: string;
  /** Включить логирование */
  enableLogging: boolean;
  /** Включить детальное логирование */
  verboseLogging: boolean;
}

/**
 * Статистика сессий
 */
export interface SessionStats {
  /** Общее количество сессий */
  totalSessions: number;
  /** Количество активных сессий */
  activeSessions: number;
  /** Количество завершенных сессий */
  completedSessions: number;
  /** Средняя продолжительность сессии (мс) */
  averageSessionDuration: number;
  /** Общее время всех сессий (мс) */
  totalSessionTime: number;
  /** Время последней сессии */
  lastSessionTime: Date | null;
  /** Время последнего обновления */
  lastUpdated: Date;
}

/**
 * События сессии
 */
export interface SessionEvent {
  /** ID сессии */
  sessionId: string;
  /** Тип события */
  type: 'sessionStarted' | 'sessionEnded' | 'modeSwitched' | 'checkpointAdded' | 'commandAdded' | 'fileChangeAdded';
  /** Время события */
  timestamp: Date;
  /** Данные события */
  data: any;
}

/**
 * Сводка по сессии
 */
export interface SessionSummary {
  /** ID сессии */
  id: string;
  /** Описание */
  description: string;
  /** Продолжительность */
  duration: string;
  /** Количество checkpoint'ов */
  checkpointsCount: number;
  /** Количество команд */
  commandsCount: number;
  /** Количество изменений файлов */
  fileChangesCount: number;
  /** Статус */
  status: string;
  /** Время начала */
  startTime: string;
  /** Время завершения */
  endTime: string | null;
}
