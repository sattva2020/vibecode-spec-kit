/**
 * Background Executor - Главный модуль для фонового выполнения команд
 */

import { BackgroundExecutor } from './core/BackgroundExecutor';
import { ProcessInfo, ProcessStatus, ProcessPriority } from './types/ExecutorTypes';

// Экспорт основных классов и типов
export { BackgroundExecutor, ProcessInfo, ProcessStatus, ProcessPriority };

// Создание глобального экземпляра BackgroundExecutor
const globalBackgroundExecutor = new BackgroundExecutor({
  maxConcurrentProcesses: 5,
  forceKillTimeout: 10000,
  autoRecovery: true,
  maxRecoveryAttempts: 3,
  verboseLogging: true
});

/**
 * Основные функции для работы с Background Executor
 */
export const backgroundExecutor = {
  /**
   * Запуск команды в фоне
   */
  async executeInBackground(
    command: string,
    args: string[] = [],
    options?: any
  ): Promise<string> {
    return await globalBackgroundExecutor.executeInBackground(command, args, options);
  },

  /**
   * Остановка процесса
   */
  async stopProcess(processId: string): Promise<boolean> {
    return await globalBackgroundExecutor.stopProcess(processId);
  },

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return globalBackgroundExecutor.getActiveProcesses();
  },

  /**
   * Получение размера очереди
   */
  getQueueSize(): number {
    return globalBackgroundExecutor.getQueueSize();
  },

  /**
   * Настройка конфигурации
   */
  configure(config: any): void {
    globalBackgroundExecutor.configure(config);
  }
};

// Автоматическая инициализация при загрузке модуля
console.log('🚀 Background Executor initialized successfully');
console.log('📊 Active processes:', backgroundExecutor.getActiveProcesses().length);

export default backgroundExecutor;
