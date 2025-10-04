/**
 * Типы данных для Process Monitor
 */

/**
 * Информация о процессе для мониторинга
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
  /** Использование CPU (%) */
  cpuUsage?: number;
  /** Использование памяти (MB) */
  memoryUsage?: number;
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
  /** Процесс приостановлен */
  PAUSED = 'paused'
}

/**
 * События Process Monitor
 */
export interface ProcessMonitorEvents {
  /** Процесс добавлен для мониторинга */
  processAdded: (processInfo: ProcessInfo) => void;
  /** Процесс удален из мониторинга */
  processRemoved: (processInfo: ProcessInfo) => void;
  /** Информация о процессе обновлена */
  processUpdated: (processInfo: ProcessInfo) => void;
  /** Процесс превысил максимальное время выполнения */
  processExceededMaxTime: (processInfo: ProcessInfo) => void;
  /** Статистика обновлена */
  statsUpdated: (stats: ProcessMonitorStats) => void;
  /** Мониторинг остановлен */
  monitoringStopped: () => void;
}

/**
 * Статистика Process Monitor
 */
export interface ProcessMonitorStats {
  /** Общее количество отслеживаемых процессов */
  totalProcesses: number;
  /** Количество активных процессов */
  activeProcesses: number;
  /** Количество завершенных процессов */
  completedProcesses: number;
  /** Количество процессов с ошибками */
  failedProcesses: number;
  /** Среднее время выполнения процессов (мс) */
  averageExecutionTime: number;
  /** Время последнего обновления */
  lastUpdated: Date;
}
