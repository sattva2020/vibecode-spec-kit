/**
 * Timeout Manager - Основной модуль для предотвращения зависания команд
 * 
 * Этот модуль предоставляет функциональность для управления таймаутами команд,
 * предотвращения зависания процессов и автоматического восстановления после ошибок.
 */

import { TimeoutManager } from './core/TimeoutManager';
import { TimeoutConfig, TimeoutResult, ProcessInfo } from './types/TimeoutTypes';

// Экспорт основных классов и типов
export { TimeoutManager, TimeoutConfig, TimeoutResult, ProcessInfo };

// Создание глобального экземпляра TimeoutManager
const globalTimeoutManager = new TimeoutManager();

/**
 * Основные функции для работы с Timeout Manager
 */
export const timeoutManager = {
  /**
   * Запуск команды с таймаутом
   */
  async executeWithTimeout(
    command: string, 
    args: string[] = [], 
    timeout: number = 30000,
    options?: Partial<TimeoutConfig>
  ): Promise<TimeoutResult> {
    return await globalTimeoutManager.executeWithTimeout(command, args, timeout, options);
  },

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return globalTimeoutManager.getActiveProcesses();
  },

  /**
   * Остановка процесса по ID
   */
  async stopProcess(processId: string): Promise<boolean> {
    return await globalTimeoutManager.stopProcess(processId);
  },

  /**
   * Получение статистики таймаутов
   */
  getTimeoutStats() {
    return globalTimeoutManager.getTimeoutStats();
  },

  /**
   * Настройка конфигурации таймаутов
   */
  configure(config: Partial<TimeoutConfig>): void {
    globalTimeoutManager.configure(config);
  }
};

// Автоматическая инициализация при загрузке модуля
console.log('🚀 Timeout Manager initialized successfully');
console.log('📊 Active processes:', timeoutManager.getActiveProcesses().length);

export default timeoutManager;
