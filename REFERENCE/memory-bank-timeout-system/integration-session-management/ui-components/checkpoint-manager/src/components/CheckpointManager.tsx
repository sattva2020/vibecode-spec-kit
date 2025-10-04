/**
 * CheckpointManager - React компонент для управления Checkpoint System
 */

import React, { useState, useEffect } from 'react';
import { 
  Save, 
  RotateCcw, 
  Trash2, 
  Clock, 
  FileText, 
  History,
  Play,
  Pause,
  Settings,
  Download,
  Upload,
  Search,
  Filter
} from 'lucide-react';

interface CheckpointInfo {
  id: string;
  timestamp: Date;
  description: string;
  currentMode: string;
  changedFiles: string[];
  metadata: Record<string, any>;
  size: number;
}

interface CheckpointManagerProps {
  onGetCheckpoints?: () => CheckpointInfo[];
  onCreateCheckpoint?: (description: string, metadata?: Record<string, any>) => Promise<string>;
  onDeleteCheckpoint?: (checkpointId: string) => Promise<boolean>;
  onRewindToCheckpoint?: (checkpoint: CheckpointInfo) => Promise<any>;
  onGetStats?: () => any;
}

export const CheckpointManager: React.FC<CheckpointManagerProps> = ({
  onGetCheckpoints,
  onCreateCheckpoint,
  onDeleteCheckpoint,
  onRewindToCheckpoint,
  onGetStats
}) => {
  const [checkpoints, setCheckpoints] = useState<CheckpointInfo[]>([]);
  const [stats, setStats] = useState<any>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMode, setSelectedMode] = useState<string>('all');
  const [isCreating, setIsCreating] = useState(false);
  const [newCheckpointDescription, setNewCheckpointDescription] = useState('');
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<CheckpointInfo | null>(null);

  // Загрузка checkpoint'ов
  const loadCheckpoints = async () => {
    if (onGetCheckpoints) {
      try {
        const loadedCheckpoints = await onGetCheckpoints();
        setCheckpoints(loadedCheckpoints);
      } catch (error) {
        console.error('Failed to load checkpoints:', error);
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
    loadCheckpoints();
    loadStats();
  }, []);

  // Фильтрация checkpoint'ов
  const filteredCheckpoints = checkpoints.filter(checkpoint => {
    const matchesSearch = checkpoint.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         checkpoint.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMode = selectedMode === 'all' || checkpoint.currentMode === selectedMode;
    return matchesSearch && matchesMode;
  });

  // Создание checkpoint'а
  const handleCreateCheckpoint = async () => {
    if (!newCheckpointDescription.trim() || !onCreateCheckpoint) return;

    try {
      setIsCreating(true);
      const checkpointId = await onCreateCheckpoint(newCheckpointDescription.trim());
      
      if (checkpointId) {
        setNewCheckpointDescription('');
        await loadCheckpoints();
        await loadStats();
      }
    } catch (error) {
      console.error('Failed to create checkpoint:', error);
    } finally {
      setIsCreating(false);
    }
  };

  // Удаление checkpoint'а
  const handleDeleteCheckpoint = async (checkpointId: string) => {
    if (!onDeleteCheckpoint) return;

    if (window.confirm('Вы уверены, что хотите удалить этот checkpoint?')) {
      try {
        const success = await onDeleteCheckpoint(checkpointId);
        
        if (success) {
          await loadCheckpoints();
          await loadStats();
        }
      } catch (error) {
        console.error('Failed to delete checkpoint:', error);
      }
    }
  };

  // Rewind к checkpoint'у
  const handleRewindToCheckpoint = async (checkpoint: CheckpointInfo) => {
    if (!onRewindToCheckpoint) return;

    if (window.confirm(`Вы уверены, что хотите откатиться к checkpoint "${checkpoint.description}"?`)) {
      try {
        const result = await onRewindToCheckpoint(checkpoint);
        
        if (result.success) {
          alert(`Успешно откатились к checkpoint! Откатано файлов: ${result.filesRewound}`);
          await loadCheckpoints();
        }
      } catch (error) {
        console.error('Failed to rewind to checkpoint:', error);
        alert('Ошибка при откате к checkpoint');
      }
    }
  };

  // Форматирование времени
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  // Форматирование размера
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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

  // Получение уникальных режимов
  const uniqueModes = Array.from(new Set(checkpoints.map(cp => cp.currentMode)));

  return (
    <div className="checkpoint-manager p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <History className="w-6 h-6 mr-2" />
          Checkpoint Manager
        </h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadCheckpoints}
            className="flex items-center px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Upload className="w-4 h-4 mr-2" />
            Обновить
          </button>
        </div>
      </div>

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <History className="w-5 h-5 text-blue-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Всего checkpoint'ов</p>
                <p className="text-2xl font-bold text-blue-600">{stats.totalCheckpoints || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-green-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Активных</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeCheckpoints || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Trash2 className="w-5 h-5 text-orange-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Удаленных</p>
                <p className="text-2xl font-bold text-orange-600">{stats.deletedCheckpoints || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Download className="w-5 h-5 text-purple-500 mr-2" />
              <div>
                <p className="text-sm text-gray-600">Общий размер</p>
                <p className="text-2xl font-bold text-purple-600">{formatSize(stats.totalSize || 0)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Создание checkpoint'а */}
      <div className="bg-gray-50 p-4 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-4">Создать новый checkpoint</h3>
        <div className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={newCheckpointDescription}
              onChange={(e) => setNewCheckpointDescription(e.target.value)}
              placeholder="Описание checkpoint'а..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isCreating}
            />
          </div>
          <button
            onClick={handleCreateCheckpoint}
            disabled={!newCheckpointDescription.trim() || isCreating}
            className="flex items-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="w-4 h-4 mr-2" />
            {isCreating ? 'Создание...' : 'Создать'}
          </button>
        </div>
      </div>

      {/* Фильтры */}
      <div className="flex space-x-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Поиск checkpoint'ов..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="w-48">
          <select
            value={selectedMode}
            onChange={(e) => setSelectedMode(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Все режимы</option>
            {uniqueModes.map(mode => (
              <option key={mode} value={mode}>{mode}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Список checkpoint'ов */}
      <div className="space-y-3">
        {filteredCheckpoints.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <History className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Нет checkpoint'ов</p>
          </div>
        ) : (
          filteredCheckpoints.map((checkpoint) => (
            <div key={checkpoint.id} className="bg-gray-50 p-4 rounded-lg border">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModeColor(checkpoint.currentMode)}`}>
                      {checkpoint.currentMode}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatTime(checkpoint.timestamp)}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatSize(checkpoint.size)}
                    </span>
                  </div>
                  <h4 className="font-medium text-gray-900 mb-1">
                    {checkpoint.description}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    ID: {checkpoint.id}
                  </p>
                  {checkpoint.changedFiles.length > 0 && (
                    <p className="text-sm text-gray-500">
                      Изменено файлов: {checkpoint.changedFiles.length}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleRewindToCheckpoint(checkpoint)}
                    className="flex items-center px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                    title="Откатиться к этому checkpoint'у"
                  >
                    <RotateCcw className="w-4 h-4 mr-1" />
                    Rewind
                  </button>
                  <button
                    onClick={() => handleDeleteCheckpoint(checkpoint.id)}
                    className="flex items-center px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                    title="Удалить checkpoint"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CheckpointManager;
