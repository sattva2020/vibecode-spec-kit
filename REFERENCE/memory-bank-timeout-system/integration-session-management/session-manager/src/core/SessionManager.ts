/**
 * SessionManager - Класс для управления сессиями разработки
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';
import { 
  SessionInfo, 
  SessionConfig, 
  SessionStats, 
  MemoryBankMode,
  SessionEvent 
} from '../types/SessionTypes';

export class SessionManager extends EventEmitter {
  private config: SessionConfig;
  private currentSession: SessionInfo | null = null;
  private sessionHistory: SessionInfo[] = [];
  private stats: SessionStats;

  constructor(config?: Partial<SessionConfig>) {
    super();
    
    this.config = {
      autoStart: true,
      autoSave: true,
      saveInterval: 30000, // 30 секунд
      maxSessions: 100,
      sessionDirectory: './sessions',
      enableLogging: true,
      verboseLogging: false,
      ...config
    };

    this.stats = {
      totalSessions: 0,
      activeSessions: 0,
      completedSessions: 0,
      averageSessionDuration: 0,
      totalSessionTime: 0,
      lastSessionTime: null,
      lastUpdated: new Date()
    };

    this.initializeSessionDirectory();
    this.loadSessionHistory();
    
    if (this.config.autoStart) {
      this.startNewSession();
    }
    
    this.log('SessionManager initialized', { config: this.config });
  }

  /**
   * Начало новой сессии
   */
  startNewSession(description?: string): SessionInfo {
    // Завершение текущей сессии если есть
    if (this.currentSession) {
      this.endCurrentSession();
    }

    const sessionId = this.generateSessionId();
    const startTime = new Date();
    
    this.currentSession = {
      id: sessionId,
      description: description || `Сессия разработки ${startTime.toLocaleString()}`,
      startTime,
      endTime: null,
      duration: 0,
      status: 'active',
      currentMode: 'VAN',
      modeHistory: [{ mode: 'VAN', timestamp: startTime, duration: 0 }],
      checkpoints: [],
      commands: [],
      fileChanges: [],
      metadata: {
        project: 'Memory Bank Timeout System',
        version: '1.0.0',
        platform: process.platform,
        nodeVersion: process.version
      }
    };

    this.sessionHistory.push(this.currentSession);
    this.stats.totalSessions++;
    this.stats.activeSessions++;
    this.stats.lastSessionTime = startTime;
    this.updateStats();

    this.log(`New session started: ${sessionId}`, {
      description: this.currentSession.description
    });

    this.emit('sessionStarted', this.currentSession);
    return this.currentSession;
  }

  /**
   * Завершение текущей сессии
   */
  endCurrentSession(): SessionInfo | null {
    if (!this.currentSession) {
      return null;
    }

    const endTime = new Date();
    this.currentSession.endTime = endTime;
    this.currentSession.duration = endTime.getTime() - this.currentSession.startTime.getTime();
    this.currentSession.status = 'completed';

    // Обновление последнего режима в истории
    if (this.currentSession.modeHistory.length > 0) {
      const lastMode = this.currentSession.modeHistory[this.currentSession.modeHistory.length - 1];
      lastMode.duration = endTime.getTime() - lastMode.timestamp.getTime();
    }

    this.stats.activeSessions--;
    this.stats.completedSessions++;
    this.updateStats();

    this.log(`Session ended: ${this.currentSession.id}`, {
      duration: this.currentSession.duration,
      checkpoints: this.currentSession.checkpoints.length,
      commands: this.currentSession.commands.length
    });

    this.emit('sessionEnded', this.currentSession);

    // Сохранение сессии
    if (this.config.autoSave) {
      this.saveSession(this.currentSession);
    }

    const completedSession = this.currentSession;
    this.currentSession = null;
    return completedSession;
  }

  /**
   * Переключение режима Memory Bank
   */
  switchMode(newMode: MemoryBankMode, description?: string): void {
    if (!this.currentSession) {
      this.log('No active session to switch mode', { newMode });
      return;
    }

    const currentTime = new Date();
    const previousMode = this.currentSession.currentMode;

    // Обновление продолжительности предыдущего режима
    if (this.currentSession.modeHistory.length > 0) {
      const lastMode = this.currentSession.modeHistory[this.currentSession.modeHistory.length - 1];
      lastMode.duration = currentTime.getTime() - lastMode.timestamp.getTime();
    }

    // Добавление нового режима в историю
    this.currentSession.modeHistory.push({
      mode: newMode,
      timestamp: currentTime,
      duration: 0
    });

    this.currentSession.currentMode = newMode;

    this.log(`Mode switched: ${previousMode} → ${newMode}`, {
      sessionId: this.currentSession.id,
      description
    });

    this.emit('modeSwitched', {
      sessionId: this.currentSession.id,
      previousMode,
      newMode,
      timestamp: currentTime,
      description
    });

    // Автоматическое сохранение при смене режима
    if (this.config.autoSave) {
      this.saveSession(this.currentSession);
    }
  }

  /**
   * Добавление checkpoint'а в сессию
   */
  addCheckpoint(checkpointId: string, description: string, metadata?: Record<string, any>): void {
    if (!this.currentSession) {
      this.log('No active session to add checkpoint', { checkpointId });
      return;
    }

    const checkpointInfo = {
      id: checkpointId,
      description,
      timestamp: new Date(),
      mode: this.currentSession.currentMode,
      metadata: metadata || {}
    };

    this.currentSession.checkpoints.push(checkpointInfo);

    this.log(`Checkpoint added to session: ${checkpointId}`, {
      sessionId: this.currentSession.id,
      description
    });

    this.emit('checkpointAdded', {
      sessionId: this.currentSession.id,
      checkpoint: checkpointInfo
    });
  }

  /**
   * Добавление команды в сессию
   */
  addCommand(command: string, result: any, executionTime: number): void {
    if (!this.currentSession) {
      this.log('No active session to add command', { command });
      return;
    }

    const commandInfo = {
      command,
      result,
      executionTime,
      timestamp: new Date(),
      mode: this.currentSession.currentMode
    };

    this.currentSession.commands.push(commandInfo);

    this.log(`Command added to session: ${command}`, {
      sessionId: this.currentSession.id,
      executionTime
    });

    this.emit('commandAdded', {
      sessionId: this.currentSession.id,
      command: commandInfo
    });
  }

  /**
   * Добавление изменения файла в сессию
   */
  addFileChange(filePath: string, changeType: 'created' | 'modified' | 'deleted'): void {
    if (!this.currentSession) {
      this.log('No active session to add file change', { filePath });
      return;
    }

    const fileChangeInfo = {
      filePath,
      changeType,
      timestamp: new Date(),
      mode: this.currentSession.currentMode
    };

    this.currentSession.fileChanges.push(fileChangeInfo);

    this.log(`File change added to session: ${filePath}`, {
      sessionId: this.currentSession.id,
      changeType
    });

    this.emit('fileChangeAdded', {
      sessionId: this.currentSession.id,
      fileChange: fileChangeInfo
    });
  }

  /**
   * Получение текущей сессии
   */
  getCurrentSession(): SessionInfo | null {
    return this.currentSession ? { ...this.currentSession } : null;
  }

  /**
   * Получение истории сессий
   */
  getSessionHistory(): SessionInfo[] {
    return [...this.sessionHistory].sort((a, b) => 
      b.startTime.getTime() - a.startTime.getTime()
    );
  }

  /**
   * Получение сессии по ID
   */
  getSession(sessionId: string): SessionInfo | null {
    return this.sessionHistory.find(session => session.id === sessionId) || null;
  }

  /**
   * Получение статистики
   */
  getStats(): SessionStats {
    return { ...this.stats };
  }

  /**
   * Сохранение сессии
   */
  async saveSession(session: SessionInfo): Promise<void> {
    try {
      const sessionData = {
        ...session,
        startTime: session.startTime.toISOString(),
        endTime: session.endTime?.toISOString(),
        modeHistory: session.modeHistory.map(mode => ({
          ...mode,
          timestamp: mode.timestamp.toISOString()
        })),
        checkpoints: session.checkpoints.map(checkpoint => ({
          ...checkpoint,
          timestamp: checkpoint.timestamp.toISOString()
        })),
        commands: session.commands.map(command => ({
          ...command,
          timestamp: command.timestamp.toISOString()
        })),
        fileChanges: session.fileChanges.map(change => ({
          ...change,
          timestamp: change.timestamp.toISOString()
        }))
      };

      const fileName = `session_${session.id}.json`;
      const filePath = path.join(this.config.sessionDirectory, fileName);
      
      fs.writeFileSync(filePath, JSON.stringify(sessionData, null, 2), 'utf8');
      
      this.log(`Session saved: ${session.id}`, { filePath });
      
    } catch (error) {
      this.log(`Failed to save session: ${session.id}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Загрузка сессии
   */
  async loadSession(sessionId: string): Promise<SessionInfo | null> {
    try {
      const fileName = `session_${sessionId}.json`;
      const filePath = path.join(this.config.sessionDirectory, fileName);
      
      if (!fs.existsSync(filePath)) {
        this.log(`Session file not found: ${sessionId}`, { filePath });
        return null;
      }

      const sessionData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      // Восстановление типов Date
      sessionData.startTime = new Date(sessionData.startTime);
      sessionData.endTime = sessionData.endTime ? new Date(sessionData.endTime) : null;
      sessionData.modeHistory = sessionData.modeHistory.map((mode: any) => ({
        ...mode,
        timestamp: new Date(mode.timestamp)
      }));
      sessionData.checkpoints = sessionData.checkpoints.map((checkpoint: any) => ({
        ...checkpoint,
        timestamp: new Date(checkpoint.timestamp)
      }));
      sessionData.commands = sessionData.commands.map((command: any) => ({
        ...command,
        timestamp: new Date(command.timestamp)
      }));
      sessionData.fileChanges = sessionData.fileChanges.map((change: any) => ({
        ...change,
        timestamp: new Date(change.timestamp)
      }));

      this.log(`Session loaded: ${sessionId}`, { filePath });
      return sessionData as SessionInfo;
      
    } catch (error) {
      this.log(`Failed to load session: ${sessionId}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return null;
    }
  }

  /**
   * Инициализация директории сессий
   */
  private initializeSessionDirectory(): void {
    if (!fs.existsSync(this.config.sessionDirectory)) {
      fs.mkdirSync(this.config.sessionDirectory, { recursive: true });
      this.log(`Session directory created: ${this.config.sessionDirectory}`);
    }
  }

  /**
   * Загрузка истории сессий
   */
  private loadSessionHistory(): void {
    try {
      if (!fs.existsSync(this.config.sessionDirectory)) {
        return;
      }

      const files = fs.readdirSync(this.config.sessionDirectory)
        .filter(file => file.startsWith('session_') && file.endsWith('.json'));

      for (const file of files) {
        const sessionId = file.replace('session_', '').replace('.json', '');
        const session = this.loadSession(sessionId);
        if (session) {
          this.sessionHistory.push(session);
        }
      }

      this.log(`Loaded ${this.sessionHistory.length} sessions from history`);
      
    } catch (error) {
      this.log(`Failed to load session history`, {
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * Обновление статистики
   */
  private updateStats(): void {
    this.stats.totalSessionTime = this.sessionHistory.reduce((total, session) => {
      return total + (session.duration || 0);
    }, 0);

    this.stats.averageSessionDuration = this.stats.completedSessions > 0 ? 
      this.stats.totalSessionTime / this.stats.completedSessions : 0;

    this.stats.lastUpdated = new Date();
  }

  /**
   * Генерация уникального ID сессии
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Настройка конфигурации
   */
  configure(config: Partial<SessionConfig>): void {
    this.config = { ...this.config, ...config };
    this.log('Configuration updated', { config: this.config });
  }

  /**
   * Логирование
   */
  private log(message: string, data?: any): void {
    if (this.config.enableLogging && this.config.verboseLogging) {
      console.log(`[SessionManager] ${message}`, data ? JSON.stringify(data, null, 2) : '');
    }
  }

  /**
   * Очистка ресурсов
   */
  destroy(): void {
    if (this.currentSession) {
      this.endCurrentSession();
    }
    
    this.sessionHistory = [];
    this.removeAllListeners();
    
    this.log('SessionManager destroyed');
  }
}
