/**
 * Типы данных для Timeout Manager
 */

/**
 * Конфигурация таймаутов
 */
export interface TimeoutConfig {
  /** Максимальное время выполнения команды по умолчанию (мс) */
  defaultTimeout: number;
  /** Максимальное количество одновременных процессов */
  maxConcurrentProcesses: number;
  /** Время ожидания перед принудительной остановкой процесса (мс) */
  forceKillTimeout: number;
  /** Включить автоматическое восстановление после ошибок */
  autoRecovery: boolean;
  /** Максимальное количество попыток восстановления */
  maxRecoveryAttempts: number;
  /** Включить детальное логирование */
  verboseLogging: boolean;
  /** Путь к файлу логов */
  logFilePath?: string;
}

/**
 * Результат выполнения команды с таймаутом
 */
export interface TimeoutResult {
  /** Успешность выполнения */
  success: boolean;
  /** Код выхода процесса */
  exitCode: number;
  /** Вывод команды (stdout) */
  stdout: string;
  /** Ошибки команды (stderr) */
  stderr: string;
  /** Время выполнения (мс) */
  executionTime: number;
  /** ID процесса */
  processId: string;
  /** Была ли команда прервана по таймауту */
  timedOut: boolean;
  /** Сообщение об ошибке */
  error?: string;
}

/**
 * Информация о процессе
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
  /** Конфигурация таймаута */
  timeoutConfig: TimeoutConfig;
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
  STOPPING = 'stopping'
}

/**
 * Статистика таймаутов
 */
export interface TimeoutStats {
  /** Общее количество выполненных команд */
  totalCommands: number;
  /** Количество успешно выполненных команд */
  successfulCommands: number;
  /** Количество команд, прерванных по таймауту */
  timedOutCommands: number;
  /** Количество команд с ошибками */
  failedCommands: number;
  /** Среднее время выполнения (мс) */
  averageExecutionTime: number;
  /** Максимальное время выполнения (мс) */
  maxExecutionTime: number;
  /** Минимальное время выполнения (мс) */
  minExecutionTime: number;
  /** Процент успешных команд */
  successRate: number;
  /** Время последнего обновления статистики */
  lastUpdated: Date;
}

/**
 * События Timeout Manager
 */
export interface TimeoutEvents {
  /** Процесс запущен */
  processStarted: (processInfo: ProcessInfo) => void;
  /** Процесс завершен */
  processCompleted: (result: TimeoutResult) => void;
  /** Процесс прерван по таймауту */
  processTimedOut: (processInfo: ProcessInfo) => void;
  /** Процесс остановлен */
  processStopped: (processInfo: ProcessInfo) => void;
  /** Ошибка в процессе */
  processError: (error: Error, processInfo: ProcessInfo) => void;
  /** Статистика обновлена */
  statsUpdated: (stats: TimeoutStats) => void;
}
