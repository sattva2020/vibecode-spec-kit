/**
 * TimeoutDashboard - React компонент для управления Command Timeout System
 */

import React, { useState, useEffect } from 'react';
import { 
  PlayCircle, 
  StopCircle, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Activity,
  Settings,
  BarChart3,
  AlertTriangle
} from 'lucide-react';

interface TimeoutStats {
  totalCommands: number;
  successfulCommands: number;
  timedOutCommands: number;
  failedCommands: number;
  averageExecutionTime: number;
  successRate: number;
}

interface ActiveProcess {
  id: string;
  command: string;
  startTime: Date;
  timeout: number;
  status: 'running' | 'completed' | 'failed' | 'timed_out';
}

interface TimeoutDashboardProps {
  onCommandExecute?: (command: string, timeout?: number) => Promise<any>;
  onGetStats?: () => TimeoutStats;
  onGetActiveProcesses?: () => ActiveProcess[];
}

export const TimeoutDashboard: React.FC<TimeoutDashboardProps> = ({
  onCommandExecute,
  onGetStats,
  onGetActiveProcesses
}) => {
  const [stats, setStats] = useState<TimeoutStats>({
    totalCommands: 0,
    successfulCommands: 0,
    timedOutCommands: 0,
    failedCommands: 0,
    averageExecutionTime: 0,
    successRate: 0
  });

  const [activeProcesses, setActiveProcesses] = useState<ActiveProcess[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  const [timeoutInput, setTimeoutInput] = useState(5000);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Обновление статистики
  const updateStats = async () => {
    if (onGetStats) {
      try {
        const newStats = await onGetStats();
        setStats(newStats);
      } catch (error) {
        console.error('Failed to get stats:', error);
      }
    }
  };

  // Обновление активных процессов
  const updateActiveProcesses = async () => {
    if (onGetActiveProcesses) {
      try {
        const processes = await onGetActiveProcesses();
        setActiveProcesses(processes);
      } catch (error) {
        console.error('Failed to get active processes:', error);
      }
    }
  };

  // Автоматическое обновление
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        updateStats();
        updateActiveProcesses();
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

  // Выполнение команды
  const handleExecuteCommand = async () => {
    if (!commandInput.trim() || !onCommandExecute) return;

    try {
      setIsRunning(true);
      await onCommandExecute(commandInput.trim(), timeoutInput);
      
      // Обновление статистики после выполнения
      setTimeout(() => {
        updateStats();
        updateActiveProcesses();
      }, 100);
      
    } catch (error) {
      console.error('Command execution failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  // Остановка мониторинга
  const handleStopMonitoring = () => {
    setIsRunning(false);
  };

  // Форматирование времени
  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  // Получение цвета статуса
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-500';
      case 'completed': return 'text-green-500';
      case 'failed': return 'text-red-500';
      case 'timed_out': return 'text-orange-500';
      default: return 'text-gray-500';
    }
  };

  // Получение иконки статуса
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="w-4 h-4 animate-pulse" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      case 'timed_out': return <AlertTriangle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="timeout-dashboard p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <Settings className="w-6 h-6 mr-2" />
          Command Timeout Dashboard
        </h2>
        <div className="flex items-center space-x-2">
          {isRunning ? (
            <button
              onClick={handleStopMonitoring}
              className="flex items-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              <StopCircle className="w-4 h-4 mr-2" />
              Остановить
            </button>
          ) : (
            <button
              onClick={() => setIsRunning(true)}
              className="flex items-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <PlayCircle className="w-4 h-4 mr-2" />
              Запустить
            </button>
          )}
        </div>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <BarChart3 className="w-5 h-5 text-blue-500 mr-2" />
            <div>
              <p className="text-sm text-gray-600">Всего команд</p>
              <p className="text-2xl font-bold text-blue-600">{stats.totalCommands}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
            <div>
              <p className="text-sm text-gray-600">Успешных</p>
              <p className="text-2xl font-bold text-green-600">{stats.successfulCommands}</p>
            </div>
          </div>
        </div>

        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
            <div>
              <p className="text-sm text-gray-600">Таймаутов</p>
              <p className="text-2xl font-bold text-orange-600">{stats.timedOutCommands}</p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center">
            <XCircle className="w-5 h-5 text-red-500 mr-2" />
            <div>
              <p className="text-sm text-gray-600">Ошибок</p>
              <p className="text-2xl font-bold text-red-600">{stats.failedCommands}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Дополнительная статистика */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Среднее время выполнения</p>
          <p className="text-xl font-bold text-gray-800">{formatTime(stats.averageExecutionTime)}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Процент успеха</p>
          <p className="text-xl font-bold text-gray-800">{stats.successRate.toFixed(1)}%</p>
        </div>
      </div>

      {/* Выполнение команды */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-4">Выполнение команды</h3>
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Команда
            </label>
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              placeholder="Введите команду (например: npm run build)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isRunning}
            />
          </div>
          <div className="w-32">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Таймаут (мс)
            </label>
            <input
              type="number"
              value={timeoutInput}
              onChange={(e) => setTimeoutInput(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isRunning}
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleExecuteCommand}
              disabled={!commandInput.trim() || isRunning}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Выполнить
            </button>
          </div>
        </div>
      </div>

      {/* Активные процессы */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Активные процессы</h3>
        {activeProcesses.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Нет активных процессов</p>
        ) : (
          <div className="space-y-2">
            {activeProcesses.map((process) => (
              <div key={process.id} className="bg-white p-3 rounded-lg border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={getStatusColor(process.status)}>
                      {getStatusIcon(process.status)}
                    </div>
                    <div>
                      <p className="font-medium">{process.command}</p>
                      <p className="text-sm text-gray-500">
                        ID: {process.id} | Таймаут: {formatTime(process.timeout)}
                      </p>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {formatTime(Date.now() - process.startTime.getTime())}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeoutDashboard;
