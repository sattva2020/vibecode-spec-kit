/**
 * Типы данных для Background Executor
 */

/**
 * Информация о процессе для фонового выполнения
 */
export interface ProcessInfo {
  /** Уникальный ID процесса */
  id: string;
  /** Команда процесса */
  command: string;
  /** Аргументы команды */
  args: string[];
  /** PID процесса в системе */
  pid?: number;
  /** Время запуска */
  startTime: Date;
  /** Статус процесса */
  status: ProcessStatus;
  /** Время выполнения (мс) */
  executionTime: number;
  /** Максимальное время выполнения (мс) */
  maxExecutionTime: number;
  /** Метаданные процесса */
  metadata?: Record<string, any>;
}

/**
 * Статусы процесса
 */
export enum ProcessStatus {
  /** Процесс запущен и выполняется */
  RUNNING = 'running',
  /** Процесс завершен успешно */
  COMPLETED = 'completed',
  /** Процесс завершен с ошибкой */
  FAILED = 'failed',
  /** Процесс прерван по таймауту */
  TIMED_OUT = 'timed_out',
  /** Процесс остановлен принудительно */
  KILLED = 'killed',
  /** Процесс в процессе остановки */
  STOPPING = 'stopping',
  /** Процесс приостановлен (в очереди) */
  PAUSED = 'paused'
}

/**
 * Приоритеты процессов
 */
export enum ProcessPriority {
  /** Низкий приоритет */
  LOW = 'low',
  /** Обычный приоритет */
  NORMAL = 'normal',
  /** Высокий приоритет */
  HIGH = 'high'
}

/**
 * Опции для фонового выполнения
 */
export interface BackgroundExecutionOptions {
  /** Таймаут выполнения (мс) */
  timeout?: number;
  /** Рабочая директория */
  workingDirectory?: string;
  /** Переменные окружения */
  env?: Record<string, string>;
  /** Приоритет процесса */
  priority?: ProcessPriority;
  /** Метаданные */
  metadata?: Record<string, any>;
}

/**
 * События Background Executor
 */
export interface BackgroundExecutorEvents {
  /** Процесс запущен */
  processStarted: (processInfo: ProcessInfo) => void;
  /** Процесс завершен */
  processCompleted: (result: BackgroundProcessResult) => void;
  /** Процесс завершен с ошибкой */
  processFailed: (error: ProcessError) => void;
  /** Процесс остановлен */
  processStopped: (processInfo: ProcessInfo) => void;
  /** Процесс добавлен в очередь */
  processQueued: (processInfo: ProcessInfo) => void;
}

/**
 * Результат выполнения фонового процесса
 */
export interface BackgroundProcessResult {
  /** Успешность выполнения */
  success: boolean;
  /** Код выхода */
  exitCode: number;
  /** Вывод команды */
  stdout: string;
  /** Ошибки команды */
  stderr: string;
  /** Время выполнения */
  executionTime: number;
  /** ID процесса */
  processId: string;
  /** Была ли команда прервана */
  interrupted: boolean;
  /** Сообщение об ошибке */
  error?: string;
}

/**
 * Ошибка процесса
 */
export interface ProcessError {
  /** Информация о процессе */
  processInfo: ProcessInfo;
  /** Сообщение об ошибке */
  error: string;
  /** Время ошибки */
  timestamp: Date;
}
