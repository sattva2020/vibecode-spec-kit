/**
 * SessionMonitor - React компонент для мониторинга сессий разработки
 */

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  Clock, 
  Activity, 
  BarChart3,
  FileText,
  Command,
  GitBranch,
  Calendar,
  Timer,
  Users,
  TrendingUp,
  TrendingDown,
  Circle
} from 'lucide-react';

interface SessionInfo {
  id: string;
  description: string;
  startTime: Date;
  endTime: Date | null;
  duration: number;
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  currentMode: string;
  modeHistory: Array<{
    mode: string;
    timestamp: Date;
    duration: number;
  }>;
  checkpoints: Array<{
    id: string;
    description: string;
    timestamp: Date;
    mode: string;
  }>;
  commands: Array<{
    command: string;
    result: any;
    executionTime: number;
    timestamp: Date;
    mode: string;
  }>;
  fileChanges: Array<{
    filePath: string;
    changeType: 'created' | 'modified' | 'deleted';
    timestamp: Date;
    mode: string;
  }>;
}

interface SessionMonitorProps {
  onGetCurrentSession?: () => SessionInfo | null;
  onGetSessionHistory?: () => SessionInfo[];
  onStartNewSession?: (description?: string) => SessionInfo;
  onEndCurrentSession?: () => SessionInfo | null;
  onSwitchMode?: (newMode: string, description?: string) => void;
  onGetStats?: () => any;
}

export const SessionMonitor: React.FC<SessionMonitorProps> = ({
  onGetCurrentSession,
  onGetSessionHistory,
  onStartNewSession,
  onEndCurrentSession,
  onSwitchMode,
  onGetStats
}) => {
  const [currentSession, setCurrentSession] = useState<SessionInfo | null>(null);
  const [sessionHistory, setSessionHistory] = useState<SessionInfo[]>([]);
  const [stats, setStats] = useState<any>({});
  const [isRunning, setIsRunning] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [selectedTab, setSelectedTab] = useState<'current' | 'history' | 'stats'>('current');

  // Загрузка текущей сессии
  const loadCurrentSession = async () => {
    if (onGetCurrentSession) {
      try {
        const session = await onGetCurrentSession();
        setCurrentSession(session);
        setIsRunning(session?.status === 'active');
      } catch (error) {
        console.error('Failed to load current session:', error);
      }
    }
  };

  // Загрузка истории сессий
  const loadSessionHistory = async () => {
    if (onGetSessionHistory) {
      try {
        const history = await onGetSessionHistory();
        setSessionHistory(history);
      } catch (error) {
        console.error('Failed to load session history:', error);
      }
    }
  };

  // Загрузка статистики
  const loadStats = async () => {
    if (onGetStats) {
      try {
        const loadedStats = await onGetStats();
        setStats(loadedStats);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    }
  };

  // Обновление данных
  useEffect(() => {
    loadCurrentSession();
    loadSessionHistory();
    loadStats();
  }, []);

  // Автоматическое обновление
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        loadCurrentSession();
        loadSessionHistory();
        loadStats();
      }, 1000);
      setRefreshInterval(interval);
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [isRunning]);

  // Начало новой сессии
  const handleStartSession = async () => {
    if (onStartNewSession) {
      try {
        const session = await onStartNewSession('Новая сессия разработки');
        setCurrentSession(session);
        setIsRunning(true);
        await loadSessionHistory();
      } catch (error) {
        console.error('Failed to start session:', error);
      }
    }
  };

  // Завершение текущей сессии
  const handleEndSession = async () => {
    if (onEndCurrentSession) {
      try {
        const endedSession = await onEndCurrentSession();
        setCurrentSession(null);
        setIsRunning(false);
        await loadSessionHistory();
        await loadStats();
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
  };

  // Переключение режима
  const handleModeSwitch = (newMode: string) => {
    if (onSwitchMode) {
      onSwitchMode(newMode, `Переключение в режим ${newMode}`);
    }
  };

  // Форматирование времени
  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
    return `${(ms / 3600000).toFixed(1)}h`;
  };

  // Форматирование даты
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  // Получение цвета статуса
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-500';
      case 'completed': return 'text-blue-500';
      case 'paused': return 'text-yellow-500';
      case 'cancelled': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  // Получение цвета режима
  const getModeColor = (mode: string) => {
    const colors = {
      'VAN': 'bg-blue-100 text-blue-800',
      'PLAN': 'bg-green-100 text-green-800',
      'CREATIVE': 'bg-purple-100 text-purple-800',
      'IMPLEMENT': 'bg-orange-100 text-orange-800',
      'REFLECT': 'bg-yellow-100 text-yellow-800',
      'ARCHIVE': 'bg-gray-100 text-gray-800'
    };
    return colors[mode as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  // Получение иконки статуса
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Circle className="w-4 h-4 fill-current" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'paused': return <Pause className="w-4 h-4" />;
      case 'cancelled': return <Square className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="session-monitor p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <Activity className="w-6 h-6 mr-2" />
          Session Monitor
        </h2>
        <div className="flex items-center space-x-2">
          {isRunning ? (
            <button
              onClick={handleEndSession}
              className="flex items-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              <Square className="w-4 h-4 mr-2" />
              Завершить
            </button>
          ) : (
            <button
              onClick={handleStartSession}
              className="flex items-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <Play className="w-4 h-4 mr-2" />
              Начать
            </button>
          )}
        </div>
      </div>

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Users className="w-5 h-5 text-blue-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Всего сессий</p>
                <p className="text-2xl font-bold text-blue-600">{stats.totalSessions || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Activity className="w-5 h-5 text-green-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Активных</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeSessions || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-purple-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Завершенных</p>
                <p className="text-2xl font-bold text-purple-600">{stats.completedSessions || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Timer className="w-5 h-5 text-orange-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Средняя продолжительность</p>
                <p className="text-2xl font-bold text-orange-600">{formatTime(stats.averageSessionDuration || 0)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Табы */}
      <div className="flex space-x-1 mb-6">
        <button
          onClick={() => setSelectedTab('current')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'current' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Текущая сессия
        </button>
        <button
          onClick={() => setSelectedTab('history')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'history' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          История
        </button>
        <button
          onClick={() => setSelectedTab('stats')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'stats' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Статистика
        </button>
      </div>

      {/* Контент табов */}
      {selectedTab === 'current' && (
        <div>
          {currentSession ? (
            <div className="space-y-4">
              {/* Информация о сессии */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">{currentSession.description}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModeColor(currentSession.currentMode)}`}>
                      {currentSession.currentMode}
                    </span>
                    <span className={getStatusColor(currentSession.status)}>
                      {getStatusIcon(currentSession.status)}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">ID сессии</p>
                    <p className="font-medium">{currentSession.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Начало</p>
                    <p className="font-medium">{formatDate(currentSession.startTime)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Продолжительность</p>
                    <p className="font-medium">{formatTime(currentSession.duration)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Режимов</p>
                    <p className="font-medium">{currentSession.modeHistory.length}</p>
                  </div>
                </div>
              </div>

              {/* Переключение режимов */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3">Переключение режимов</h4>
                <div className="flex flex-wrap gap-2">
                  {['VAN', 'PLAN', 'CREATIVE', 'IMPLEMENT', 'REFLECT', 'ARCHIVE'].map(mode => (
                    <button
                      key={mode}
                      onClick={() => handleModeSwitch(mode)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        mode === currentSession.currentMode
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
              </div>

              {/* Статистика сессии */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <FileText className="w-6 h-6 mx-auto mb-2 text-blue-500" />
                  <p className="text-2xl font-bold text-blue-600">{currentSession.checkpoints.length}</p>
                  <p className="text-sm text-gray-600">Checkpoint'ов</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <Command className="w-6 h-6 mx-auto mb-2 text-green-500" />
                  <p className="text-2xl font-bold text-green-600">{currentSession.commands.length}</p>
                  <p className="text-sm text-gray-600">Команд</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <GitBranch className="w-6 h-6 mx-auto mb-2 text-purple-500" />
                  <p className="text-2xl font-bold text-purple-600">{currentSession.fileChanges.length}</p>
                  <p className="text-sm text-gray-600">Изменений файлов</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Нет активной сессии</p>
              <p className="text-sm">Нажмите "Начать" для создания новой сессии</p>
            </div>
          )}
        </div>
      )}

      {selectedTab === 'history' && (
        <div className="space-y-3">
          {sessionHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Нет истории сессий</p>
            </div>
          ) : (
            sessionHistory.map((session) => (
              <div key={session.id} className="bg-gray-50 p-4 rounded-lg border">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{session.description}</h4>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModeColor(session.currentMode)}`}>
                      {session.currentMode}
                    </span>
                    <span className={getStatusColor(session.status)}>
                      {getStatusIcon(session.status)}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Продолжительность</p>
                    <p className="font-medium">{formatTime(session.duration)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Checkpoint'ов</p>
                    <p className="font-medium">{session.checkpoints.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Команд</p>
                    <p className="font-medium">{session.commands.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Изменений файлов</p>
                    <p className="font-medium">{session.fileChanges.length}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {selectedTab === 'stats' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Общая статистика</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Всего сессий:</span>
                  <span className="font-medium">{stats.totalSessions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Активных сессий:</span>
                  <span className="font-medium">{stats.activeSessions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Завершенных сессий:</span>
                  <span className="font-medium">{stats.completedSessions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Общее время:</span>
                  <span className="font-medium">{formatTime(stats.totalSessionTime || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Средняя продолжительность:</span>
                  <span className="font-medium">{formatTime(stats.averageSessionDuration || 0)}</span>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Тренды</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center">
                  <TrendingUp className="w-4 h-4 text-green-500 mr-2" />
                  <span>Рост активности</span>
                </div>
                <div className="flex items-center">
                  <TrendingDown className="w-4 h-4 text-red-500 mr-2" />
                  <span>Снижение ошибок</span>
                </div>
                <div className="flex items-center">
                  <TrendingUp className="w-4 h-4 text-blue-500 mr-2" />
                  <span>Увеличение производительности</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionMonitor;
