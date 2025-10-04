/**
 * Process Monitor - Главный модуль для мониторинга процессов
 */

import { ProcessMonitor } from './core/ProcessMonitor';
import { ProcessInfo, ProcessStatus } from './types/ProcessTypes';

// Экспорт основных классов и типов
export { ProcessMonitor, ProcessInfo, ProcessStatus };

// Создание глобального экземпляра ProcessMonitor
const globalProcessMonitor = new ProcessMonitor({
  updateInterval: 1000,
  historyRetentionTime: 3600000,
  verboseLogging: true,
  maxHistorySize: 1000
});

/**
 * Основные функции для работы с Process Monitor
 */
export const processMonitor = {
  /**
   * Добавление процесса для мониторинга
   */
  addProcess(processInfo: ProcessInfo): void {
    globalProcessMonitor.addProcess(processInfo);
  },

  /**
   * Удаление процесса из мониторинга
   */
  removeProcess(processId: string): void {
    globalProcessMonitor.removeProcess(processId);
  },

  /**
   * Обновление информации о процессе
   */
  updateProcess(processId: string, updates: Partial<ProcessInfo>): void {
    globalProcessMonitor.updateProcess(processId, updates);
  },

  /**
   * Получение информации о процессе
   */
  getProcess(processId: string): ProcessInfo | undefined {
    return globalProcessMonitor.getProcess(processId);
  },

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return globalProcessMonitor.getActiveProcesses();
  },

  /**
   * Получение истории процессов
   */
  getProcessHistory(): ProcessInfo[] {
    return globalProcessMonitor.getProcessHistory();
  },

  /**
   * Получение статистики мониторинга
   */
  getStats() {
    return globalProcessMonitor.getStats();
  },

  /**
   * Настройка конфигурации
   */
  configure(config: any): void {
    globalProcessMonitor.configure(config);
  }
};

// Автоматическая инициализация при загрузке модуля
console.log('🚀 Process Monitor initialized successfully');
console.log('📊 Active processes:', processMonitor.getActiveProcesses().length);

export default processMonitor;
