/**
 * Integration Layer - Главный модуль интеграции с Memory Bank
 */

import { MemoryBankIntegration } from './core/MemoryBankIntegration';

// Экспорт основных классов
export { MemoryBankIntegration };

// Создание глобального экземпляра интеграции
const globalIntegration = new MemoryBankIntegration({
  autoCheckpoints: true,
  checkpointInterval: 300000, // 5 минут
  maxCheckpoints: 50,
  fileMonitoring: true,
  workflowIntegration: true,
  verboseLogging: true
});

/**
 * Основные функции для работы с Integration Layer
 */
export const memoryBankIntegration = {
  /**
   * Выполнение команды с таймаутом
   */
  async executeCommand(
    command: string,
    args: string[] = [],
    timeout?: number
  ): Promise<any> {
    return await globalIntegration.executeCommand(command, args, timeout);
  },

  /**
   * Запуск команды в фоне
   */
  async executeInBackground(
    command: string,
    args: string[] = [],
    options?: any
  ): Promise<string> {
    return await globalIntegration.executeInBackground(command, args, options);
  },

  /**
   * Переключение режима Memory Bank
   */
  switchMode(newMode: string): void {
    globalIntegration.switchMode(newMode);
  },

  /**
   * Создание checkpoint'а
   */
  createCheckpoint(description: string, metadata?: Record<string, any>): string {
    return globalIntegration.createCheckpoint(description, metadata);
  },

  /**
   * Получение статистики системы
   */
  getStats() {
    return globalIntegration.getIntegrationStats();
  },

  /**
   * Получение списка checkpoint'ов
   */
  getCheckpoints() {
    return globalIntegration.getCheckpoints();
  },

  /**
   * Настройка конфигурации
   */
  configure(config: any): void {
    globalIntegration.configure(config);
  }
};

// Автоматическая инициализация при загрузке модуля
console.log('🚀 Integration Layer initialized successfully');
console.log('📊 System stats:', memoryBankIntegration.getStats());

export default memoryBankIntegration;
