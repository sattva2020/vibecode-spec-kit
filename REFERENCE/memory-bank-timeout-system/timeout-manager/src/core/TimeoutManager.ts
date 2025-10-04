/**
 * TimeoutManager - Основной класс для управления таймаутами команд
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import { 
  TimeoutConfig, 
  TimeoutResult, 
  ProcessInfo, 
  ProcessStatus, 
  TimeoutStats,
  TimeoutEvents 
} from '../types/TimeoutTypes';

export class TimeoutManager extends EventEmitter {
  private config: TimeoutConfig;
  private activeProcesses: Map<string, ProcessInfo> = new Map();
  private processTimeouts: Map<string, NodeJS.Timeout> = new Map();
  private stats: TimeoutStats;

  constructor(config?: Partial<TimeoutConfig>) {
    super();
    
    // Конфигурация по умолчанию
    this.config = {
      defaultTimeout: 30000, // 30 секунд
      maxConcurrentProcesses: 10,
      forceKillTimeout: 5000, // 5 секунд
      autoRecovery: true,
      maxRecoveryAttempts: 3,
      verboseLogging: false,
      ...config
    };

    // Инициализация статистики
    this.stats = {
      totalCommands: 0,
      successfulCommands: 0,
      timedOutCommands: 0,
      failedCommands: 0,
      averageExecutionTime: 0,
      maxExecutionTime: 0,
      minExecutionTime: Infinity,
      successRate: 0,
      lastUpdated: new Date()
    };

    this.log('TimeoutManager initialized', { config: this.config });
  }

  /**
   * Выполнение команды с таймаутом
   */
  async executeWithTimeout(
    command: string,
    args: string[] = [],
    timeout: number = this.config.defaultTimeout,
    options?: Partial<TimeoutConfig>
  ): Promise<TimeoutResult> {
    const processId = this.generateProcessId();
    const startTime = Date.now();
    
    // Проверка лимита одновременных процессов
    if (this.activeProcesses.size >= this.config.maxConcurrentProcesses) {
      throw new Error(`Maximum concurrent processes limit reached: ${this.config.maxConcurrentProcesses}`);
    }

    this.log(`Executing command: ${command} ${args.join(' ')}`, { processId, timeout });

    try {
      // Создание процесса
      const childProcess = spawn(command, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: true
      });

      // Создание информации о процессе
      const processInfo: ProcessInfo = {
        id: processId,
        command,
        args,
        pid: childProcess.pid,
        startTime: new Date(),
        status: ProcessStatus.RUNNING,
        executionTime: 0,
        maxExecutionTime: timeout,
        timeoutConfig: { ...this.config, ...options }
      };

      // Добавление процесса в активные
      this.activeProcesses.set(processId, processInfo);
      this.emit('processStarted', processInfo);

      // Создание Promise для результата
      const result = await this.createProcessPromise(childProcess, processInfo, timeout);
      
      // Обновление статистики
      this.updateStats(result);
      
      // Удаление процесса из активных
      this.activeProcesses.delete(processId);
      
      this.log(`Command completed: ${command}`, { 
        processId, 
        success: result.success, 
        executionTime: result.executionTime 
      });

      return result;

    } catch (error) {
      const executionTime = Date.now() - startTime;
      
      // Создание результата с ошибкой
      const errorResult: TimeoutResult = {
        success: false,
        exitCode: -1,
        stdout: '',
        stderr: error instanceof Error ? error.message : String(error),
        executionTime,
        processId,
        timedOut: false,
        error: error instanceof Error ? error.message : String(error)
      };

      this.updateStats(errorResult);
      
      this.log(`Command failed: ${command}`, { processId, error: errorResult.error });
      
      return errorResult;
    }
  }

  /**
   * Создание Promise для процесса с таймаутом
   */
  private createProcessPromise(
    childProcess: ChildProcess,
    processInfo: ProcessInfo,
    timeout: number
  ): Promise<TimeoutResult> {
    return new Promise((resolve) => {
      let stdout = '';
      let stderr = '';
      let resolved = false;
      const startTime = Date.now();

      // Обработка вывода процесса
      childProcess.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      childProcess.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      // Обработка завершения процесса
      childProcess.on('close', (code) => {
        if (resolved) return;
        resolved = true;

        const executionTime = Date.now() - startTime;
        processInfo.status = code === 0 ? ProcessStatus.COMPLETED : ProcessStatus.FAILED;
        processInfo.executionTime = executionTime;

        // Очистка таймаута
        const timeoutId = this.processTimeouts.get(processInfo.id);
        if (timeoutId) {
          clearTimeout(timeoutId);
          this.processTimeouts.delete(processInfo.id);
        }

        const result: TimeoutResult = {
          success: code === 0,
          exitCode: code || 0,
          stdout,
          stderr,
          executionTime,
          processId: processInfo.id,
          timedOut: false
        };

        this.emit('processCompleted', result);
        resolve(result);
      });

      // Обработка ошибок процесса
      childProcess.on('error', (error) => {
        if (resolved) return;
        resolved = true;

        const executionTime = Date.now() - startTime;
        processInfo.status = ProcessStatus.FAILED;
        processInfo.executionTime = executionTime;

        // Очистка таймаута
        const timeoutId = this.processTimeouts.get(processInfo.id);
        if (timeoutId) {
          clearTimeout(timeoutId);
          this.processTimeouts.delete(processInfo.id);
        }

        const result: TimeoutResult = {
          success: false,
          exitCode: -1,
          stdout,
          stderr,
          executionTime,
          processId: processInfo.id,
          timedOut: false,
          error: error.message
        };

        this.emit('processError', error, processInfo);
        resolve(result);
      });

      // Установка таймаута
      const timeoutId = setTimeout(() => {
        if (resolved) return;
        resolved = true;

        const executionTime = Date.now() - startTime;
        processInfo.status = ProcessStatus.TIMED_OUT;
        processInfo.executionTime = executionTime;

        this.log(`Process timed out: ${processInfo.command}`, { processId: processInfo.id });
        
        // Принудительная остановка процесса
        this.killProcess(childProcess, processInfo);

        const result: TimeoutResult = {
          success: false,
          exitCode: -1,
          stdout,
          stderr,
          executionTime,
          processId: processInfo.id,
          timedOut: true,
          error: `Process timed out after ${timeout}ms`
        };

        this.emit('processTimedOut', processInfo);
        resolve(result);
      }, timeout);

      this.processTimeouts.set(processInfo.id, timeoutId);
    });
  }

  /**
   * Принудительная остановка процесса
   */
  private killProcess(childProcess: ChildProcess, processInfo: ProcessInfo): void {
    try {
      processInfo.status = ProcessStatus.STOPPING;
      
      // Сначала попытка graceful shutdown
      childProcess.kill('SIGTERM');
      
      // Если процесс не завершился, принудительная остановка
      setTimeout(() => {
        if (!childProcess.killed) {
          childProcess.kill('SIGKILL');
          processInfo.status = ProcessStatus.KILLED;
          this.log(`Process force killed: ${processInfo.command}`, { processId: processInfo.id });
        }
      }, this.config.forceKillTimeout);
      
    } catch (error) {
      this.log(`Error killing process: ${processInfo.command}`, { 
        processId: processInfo.id, 
        error: error instanceof Error ? error.message : String(error) 
      });
    }
  }

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return Array.from(this.activeProcesses.values());
  }

  /**
   * Остановка процесса по ID
   */
  async stopProcess(processId: string): Promise<boolean> {
    const processInfo = this.activeProcesses.get(processId);
    if (!processInfo) {
      return false;
    }

    // Очистка таймаута
    const timeoutId = this.processTimeouts.get(processId);
    if (timeoutId) {
      clearTimeout(timeoutId);
      this.processTimeouts.delete(processId);
    }

    // Остановка процесса
    processInfo.status = ProcessStatus.STOPPING;
    this.emit('processStopped', processInfo);
    
    // Удаление из активных процессов
    this.activeProcesses.delete(processId);
    
    return true;
  }

  /**
   * Получение статистики таймаутов
   */
  getTimeoutStats(): TimeoutStats {
    return { ...this.stats };
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<TimeoutConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Обновление статистики
   */
  private updateStats(result: TimeoutResult): void {
    this.stats.totalCommands++;
    
    if (result.success) {
      this.stats.successfulCommands++;
    } else if (result.timedOut) {
      this.stats.timedOutCommands++;
    } else {
      this.stats.failedCommands++;
    }

    // Обновление времени выполнения
    if (result.executionTime > this.stats.maxExecutionTime) {
      this.stats.maxExecutionTime = result.executionTime;
    }
    
    if (result.executionTime < this.stats.minExecutionTime) {
      this.stats.minExecutionTime = result.executionTime;
    }

    // Пересчет среднего времени
    const totalTime = this.stats.averageExecutionTime * (this.stats.totalCommands - 1) + result.executionTime;
    this.stats.averageExecutionTime = totalTime / this.stats.totalCommands;

    // Пересчет процента успешности
    this.stats.successRate = (this.stats.successfulCommands / this.stats.totalCommands) * 100;
    
    this.stats.lastUpdated = new Date();
    this.emit('statsUpdated', this.stats);
  }

  /**
   * Генерация уникального ID процесса
   */
  private generateProcessId(): string {
    return `process_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[TimeoutManager] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }
}
