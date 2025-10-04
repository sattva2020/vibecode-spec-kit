/**
 * ProcessMonitor - Класс для мониторинга выполнения команд в реальном времени
 */

import { EventEmitter } from 'events';
import { ProcessInfo, ProcessStatus } from '../types/ProcessTypes';

export interface ProcessMonitorConfig {
  /** Интервал обновления статуса процессов (мс) */
  updateInterval: number;
  /** Максимальное время хранения истории процессов (мс) */
  historyRetentionTime: number;
  /** Включить детальное логирование */
  verboseLogging: boolean;
  /** Максимальное количество процессов в истории */
  maxHistorySize: number;
}

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

export class ProcessMonitor extends EventEmitter {
  private config: ProcessMonitorConfig;
  private activeProcesses: Map<string, ProcessInfo> = new Map();
  private processHistory: ProcessInfo[] = [];
  private stats: ProcessMonitorStats;
  private updateInterval: NodeJS.Timeout | null = null;

  constructor(config?: Partial<ProcessMonitorConfig>) {
    super();
    
    this.config = {
      updateInterval: 1000, // 1 секунда
      historyRetentionTime: 3600000, // 1 час
      verboseLogging: false,
      maxHistorySize: 1000,
      ...config
    };

    this.stats = {
      totalProcesses: 0,
      activeProcesses: 0,
      completedProcesses: 0,
      failedProcesses: 0,
      averageExecutionTime: 0,
      lastUpdated: new Date()
    };

    this.startMonitoring();
    this.log('ProcessMonitor initialized', { config: this.config });
  }

  /**
   * Добавление процесса для мониторинга
   */
  addProcess(processInfo: ProcessInfo): void {
    this.activeProcesses.set(processInfo.id, processInfo);
    this.stats.totalProcesses++;
    this.updateStats();
    
    this.log(`Process added for monitoring: ${processInfo.command}`, { 
      processId: processInfo.id,
      pid: processInfo.pid 
    });
    
    this.emit('processAdded', processInfo);
  }

  /**
   * Удаление процесса из мониторинга
   */
  removeProcess(processId: string): void {
    const processInfo = this.activeProcesses.get(processId);
    if (processInfo) {
      this.activeProcesses.delete(processId);
      
      // Добавление в историю
      this.addToHistory(processInfo);
      
      this.log(`Process removed from monitoring: ${processInfo.command}`, { 
        processId: processInfo.id,
        status: processInfo.status,
        executionTime: processInfo.executionTime
      });
      
      this.emit('processRemoved', processInfo);
    }
  }

  /**
   * Обновление информации о процессе
   */
  updateProcess(processId: string, updates: Partial<ProcessInfo>): void {
    const processInfo = this.activeProcesses.get(processId);
    if (processInfo) {
      // Обновление информации
      Object.assign(processInfo, updates);
      
      // Обновление времени выполнения
      if (processInfo.status === ProcessStatus.RUNNING) {
        processInfo.executionTime = Date.now() - processInfo.startTime.getTime();
      }
      
      this.log(`Process updated: ${processInfo.command}`, { 
        processId: processInfo.id,
        updates: Object.keys(updates),
        executionTime: processInfo.executionTime
      });
      
      this.emit('processUpdated', processInfo);
    }
  }

  /**
   * Получение информации о процессе
   */
  getProcess(processId: string): ProcessInfo | undefined {
    return this.activeProcesses.get(processId);
  }

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return Array.from(this.activeProcesses.values());
  }

  /**
   * Получение истории процессов
   */
  getProcessHistory(): ProcessInfo[] {
    return [...this.processHistory];
  }

  /**
   * Получение статистики мониторинга
   */
  getStats(): ProcessMonitorStats {
    return { ...this.stats };
  }

  /**
   * Запуск мониторинга
   */
  private startMonitoring(): void {
    this.updateInterval = setInterval(() => {
      this.updateProcesses();
      this.cleanupHistory();
      this.updateStats();
    }, this.config.updateInterval);
  }

  /**
   * Остановка мониторинга
   */
  stopMonitoring(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
    
    this.log('Process monitoring stopped');
    this.emit('monitoringStopped');
  }

  /**
   * Обновление процессов
   */
  private updateProcesses(): void {
    const now = Date.now();
    
    for (const [processId, processInfo] of this.activeProcesses) {
      if (processInfo.status === ProcessStatus.RUNNING) {
        // Обновление времени выполнения
        processInfo.executionTime = now - processInfo.startTime.getTime();
        
        // Проверка на превышение максимального времени выполнения
        if (processInfo.executionTime > processInfo.maxExecutionTime) {
          this.log(`Process exceeded max execution time: ${processInfo.command}`, {
            processId: processInfo.id,
            executionTime: processInfo.executionTime,
            maxExecutionTime: processInfo.maxExecutionTime
          });
          
          this.emit('processExceededMaxTime', processInfo);
        }
      }
    }
  }

  /**
   * Очистка истории процессов
   */
  private cleanupHistory(): void {
    const now = Date.now();
    const cutoffTime = now - this.config.historyRetentionTime;
    
    // Удаление старых записей
    this.processHistory = this.processHistory.filter(
      process => process.startTime.getTime() > cutoffTime
    );
    
    // Ограничение размера истории
    if (this.processHistory.length > this.config.maxHistorySize) {
      this.processHistory = this.processHistory.slice(-this.config.maxHistorySize);
    }
  }

  /**
   * Добавление процесса в историю
   */
  private addToHistory(processInfo: ProcessInfo): void {
    this.processHistory.push({ ...processInfo });
    
    // Ограничение размера истории
    if (this.processHistory.length > this.config.maxHistorySize) {
      this.processHistory.shift();
    }
  }

  /**
   * Обновление статистики
   */
  private updateStats(): void {
    const activeProcesses = Array.from(this.activeProcesses.values());
    const completedProcesses = this.processHistory.filter(
      p => p.status === ProcessStatus.COMPLETED
    );
    const failedProcesses = this.processHistory.filter(
      p => p.status === ProcessStatus.FAILED || p.status === ProcessStatus.TIMED_OUT
    );
    
    this.stats.activeProcesses = activeProcesses.length;
    this.stats.completedProcesses = completedProcesses.length;
    this.stats.failedProcesses = failedProcesses.length;
    
    // Расчет среднего времени выполнения
    const allProcesses = [...completedProcesses, ...failedProcesses];
    if (allProcesses.length > 0) {
      const totalTime = allProcesses.reduce((sum, p) => sum + p.executionTime, 0);
      this.stats.averageExecutionTime = totalTime / allProcesses.length;
    }
    
    this.stats.lastUpdated = new Date();
    this.emit('statsUpdated', this.stats);
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<ProcessMonitorConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[ProcessMonitor] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    this.stopMonitoring();
    this.activeProcesses.clear();
    this.processHistory = [];
    this.removeAllListeners();
    
    this.log('ProcessMonitor destroyed');
  }
}
