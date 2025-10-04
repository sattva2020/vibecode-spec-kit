/**
 * BackgroundExecutor - Класс для безопасного выполнения команд в фоне
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import { ProcessInfo, ProcessStatus } from '../types/ExecutorTypes';

export interface BackgroundExecutorConfig {
  /** Максимальное количество одновременных фоновых процессов */
  maxConcurrentProcesses: number;
  /** Время ожидания перед принудительной остановкой (мс) */
  forceKillTimeout: number;
  /** Включить автоматическое восстановление */
  autoRecovery: boolean;
  /** Максимальное количество попыток восстановления */
  maxRecoveryAttempts: number;
  /** Включить детальное логирование */
  verboseLogging: boolean;
  /** Рабочая директория для процессов */
  workingDirectory?: string;
}

export interface BackgroundProcess {
  /** ID процесса */
  id: string;
  /** Команда */
  command: string;
  /** Аргументы */
  args: string[];
  /** Child process */
  process: ChildProcess;
  /** Информация о процессе */
  info: ProcessInfo;
  /** Promise для результата */
  promise: Promise<BackgroundProcessResult>;
  /** Время запуска */
  startTime: Date;
  /** Попытки восстановления */
  recoveryAttempts: number;
}

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

export class BackgroundExecutor extends EventEmitter {
  private config: BackgroundExecutorConfig;
  private activeProcesses: Map<string, BackgroundProcess> = new Map();
  private processQueue: BackgroundProcess[] = [];

  constructor(config?: Partial<BackgroundExecutorConfig>) {
    super();
    
    this.config = {
      maxConcurrentProcesses: 5,
      forceKillTimeout: 10000, // 10 секунд
      autoRecovery: true,
      maxRecoveryAttempts: 3,
      verboseLogging: false,
      ...config
    };

    this.log('BackgroundExecutor initialized', { config: this.config });
  }

  /**
   * Запуск команды в фоне
   */
  async executeInBackground(
    command: string,
    args: string[] = [],
    options?: {
      timeout?: number;
      workingDirectory?: string;
      env?: Record<string, string>;
      priority?: 'low' | 'normal' | 'high';
    }
  ): Promise<string> {
    const processId = this.generateProcessId();
    
    // Проверка лимита процессов
    if (this.activeProcesses.size >= this.config.maxConcurrentProcesses) {
      // Добавление в очередь
      return this.queueProcess(command, args, options);
    }

    return this.startProcess(processId, command, args, options);
  }

  /**
   * Запуск процесса
   */
  private async startProcess(
    processId: string,
    command: string,
    args: string[] = [],
    options?: any
  ): Promise<string> {
    this.log(`Starting background process: ${command}`, { processId, args });

    try {
      // Создание процесса
      const childProcess = spawn(command, args, {
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true,
        cwd: options?.workingDirectory || this.config.workingDirectory,
        env: { ...process.env, ...options?.env }
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
        maxExecutionTime: options?.timeout || 300000, // 5 минут по умолчанию
        metadata: {
          priority: options?.priority || 'normal',
          workingDirectory: options?.workingDirectory,
          env: options?.env
        }
      };

      // Создание Promise для результата
      const promise = this.createProcessPromise(childProcess, processInfo);

      // Создание объекта фонового процесса
      const backgroundProcess: BackgroundProcess = {
        id: processId,
        command,
        args,
        process: childProcess,
        info: processInfo,
        promise,
        startTime: new Date(),
        recoveryAttempts: 0
      };

      // Добавление в активные процессы
      this.activeProcesses.set(processId, backgroundProcess);
      this.emit('processStarted', processInfo);

      // Обработка завершения процесса
      promise.then((result) => {
        this.handleProcessCompletion(backgroundProcess, result);
      }).catch((error) => {
        this.handleProcessError(backgroundProcess, error);
      });

      return processId;

    } catch (error) {
      this.log(`Failed to start process: ${command}`, { 
        processId, 
        error: error instanceof Error ? error.message : String(error) 
      });
      throw error;
    }
  }

  /**
   * Создание Promise для процесса
   */
  private createProcessPromise(
    childProcess: ChildProcess,
    processInfo: ProcessInfo
  ): Promise<BackgroundProcessResult> {
    return new Promise((resolve, reject) => {
      let stdout = '';
      let stderr = '';
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
        const executionTime = Date.now() - startTime;
        processInfo.status = code === 0 ? ProcessStatus.COMPLETED : ProcessStatus.FAILED;
        processInfo.executionTime = executionTime;

        const result: BackgroundProcessResult = {
          success: code === 0,
          exitCode: code || 0,
          stdout,
          stderr,
          executionTime,
          processId: processInfo.id,
          interrupted: false
        };

        resolve(result);
      });

      // Обработка ошибок процесса
      childProcess.on('error', (error) => {
        const executionTime = Date.now() - startTime;
        processInfo.status = ProcessStatus.FAILED;
        processInfo.executionTime = executionTime;

        const result: BackgroundProcessResult = {
          success: false,
          exitCode: -1,
          stdout,
          stderr,
          executionTime,
          processId: processInfo.id,
          interrupted: true,
          error: error.message
        };

        reject(result);
      });
    });
  }

  /**
   * Обработка завершения процесса
   */
  private handleProcessCompletion(
    backgroundProcess: BackgroundProcess,
    result: BackgroundProcessResult
  ): void {
    this.activeProcesses.delete(backgroundProcess.id);
    
    this.log(`Process completed: ${backgroundProcess.command}`, {
      processId: backgroundProcess.id,
      success: result.success,
      executionTime: result.executionTime
    });

    this.emit('processCompleted', result);

    // Запуск следующего процесса из очереди
    this.processNextInQueue();
  }

  /**
   * Обработка ошибки процесса
   */
  private handleProcessError(
    backgroundProcess: BackgroundProcess,
    error: BackgroundProcessResult | Error
  ): void {
    this.activeProcesses.delete(backgroundProcess.id);
    
    // Попытка восстановления
    if (this.config.autoRecovery && 
        backgroundProcess.recoveryAttempts < this.config.maxRecoveryAttempts) {
      
      backgroundProcess.recoveryAttempts++;
      this.log(`Attempting recovery for process: ${backgroundProcess.command}`, {
        processId: backgroundProcess.id,
        attempt: backgroundProcess.recoveryAttempts
      });

      // Перезапуск процесса
      setTimeout(() => {
        this.startProcess(
          backgroundProcess.id,
          backgroundProcess.command,
          backgroundProcess.args
        );
      }, 1000 * backgroundProcess.recoveryAttempts); // Экспоненциальная задержка
    } else {
      this.log(`Process failed: ${backgroundProcess.command}`, {
        processId: backgroundProcess.id,
        error: error instanceof Error ? error.message : error.error
      });

      this.emit('processFailed', {
        processInfo: backgroundProcess.info,
        error: error instanceof Error ? error.message : error.error
      });
    }

    // Запуск следующего процесса из очереди
    this.processNextInQueue();
  }

  /**
   * Добавление процесса в очередь
   */
  private queueProcess(
    command: string,
    args: string[],
    options?: any
  ): string {
    const processId = this.generateProcessId();
    
    const queuedProcess: BackgroundProcess = {
      id: processId,
      command,
      args,
      process: null as any, // Будет создан при запуске
      info: {
        id: processId,
        command,
        args,
        startTime: new Date(),
        status: ProcessStatus.PAUSED,
        executionTime: 0,
        maxExecutionTime: options?.timeout || 300000,
        metadata: options
      },
      promise: Promise.resolve(),
      startTime: new Date(),
      recoveryAttempts: 0
    };

    this.processQueue.push(queuedProcess);
    
    this.log(`Process queued: ${command}`, { processId });
    this.emit('processQueued', queuedProcess.info);

    return processId;
  }

  /**
   * Обработка следующего процесса в очереди
   */
  private processNextInQueue(): void {
    if (this.processQueue.length > 0 && 
        this.activeProcesses.size < this.config.maxConcurrentProcesses) {
      
      const queuedProcess = this.processQueue.shift()!;
      this.startProcess(
        queuedProcess.id,
        queuedProcess.command,
        queuedProcess.args,
        queuedProcess.info.metadata
      );
    }
  }

  /**
   * Остановка процесса
   */
  async stopProcess(processId: string): Promise<boolean> {
    const backgroundProcess = this.activeProcesses.get(processId);
    if (!backgroundProcess) {
      return false;
    }

    this.log(`Stopping process: ${backgroundProcess.command}`, { processId });

    try {
      // Graceful shutdown
      backgroundProcess.process.kill('SIGTERM');
      
      // Принудительная остановка если не завершился
      setTimeout(() => {
        if (!backgroundProcess.process.killed) {
          backgroundProcess.process.kill('SIGKILL');
          backgroundProcess.info.status = ProcessStatus.KILLED;
        }
      }, this.config.forceKillTimeout);

      this.activeProcesses.delete(processId);
      this.emit('processStopped', backgroundProcess.info);
      
      return true;
    } catch (error) {
      this.log(`Error stopping process: ${backgroundProcess.command}`, {
        processId,
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Получение списка активных процессов
   */
  getActiveProcesses(): ProcessInfo[] {
    return Array.from(this.activeProcesses.values()).map(p => p.info);
  }

  /**
   * Получение размера очереди
   */
  getQueueSize(): number {
    return this.processQueue.length;
  }

  /**
   * Генерация уникального ID процесса
   */
  private generateProcessId(): string {
    return `bg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<BackgroundExecutorConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.verboseLogging) {
      console.log(`[BackgroundExecutor] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    // Остановка всех активных процессов
    for (const [processId, backgroundProcess] of this.activeProcesses) {
      this.stopProcess(processId);
    }

    // Очистка очереди
    this.processQueue = [];
    this.activeProcesses.clear();
    this.removeAllListeners();
    
    this.log('BackgroundExecutor destroyed');
  }
}
