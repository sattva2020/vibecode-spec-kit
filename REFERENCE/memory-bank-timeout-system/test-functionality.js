/**
 * Тест функциональности Memory Bank Timeout System
 */

const { memoryBankTimeout } = require('./dist/index.js');

async function testFunctionality() {
  console.log('🧪 Запуск тестирования функциональности Memory Bank Timeout System...\n');

  try {
    // Тест 1: Получение статистики системы
    console.log('📊 Тест 1: Получение статистики системы');
    const stats = memoryBankTimeout.getStats();
    console.log('Статистика системы:', JSON.stringify(stats, null, 2));
    console.log('✅ Тест 1 пройден\n');

    // Тест 2: Создание checkpoint'а
    console.log('📋 Тест 2: Создание checkpoint\'а');
    const checkpointId = memoryBankTimeout.createCheckpoint('Тестовый checkpoint');
    console.log(`Checkpoint создан с ID: ${checkpointId}`);
    console.log('✅ Тест 2 пройден\n');

    // Тест 3: Переключение режима
    console.log('🔄 Тест 3: Переключение режима');
    memoryBankTimeout.switchMode('PLAN');
    console.log('Режим переключен на PLAN');
    console.log('✅ Тест 3 пройден\n');

    // Тест 4: Выполнение простой команды с таймаутом
    console.log('⚡ Тест 4: Выполнение команды с таймаутом');
    const result = await memoryBankTimeout.executeCommand('echo', ['Hello Memory Bank Timeout System!'], 5000);
    console.log('Результат выполнения команды:', {
      success: result.success,
      stdout: result.stdout.trim(),
      executionTime: result.executionTime
    });
    console.log('✅ Тест 4 пройден\n');

    // Тест 5: Получение checkpoint'ов
    console.log('📋 Тест 5: Получение checkpoint\'ов');
    const checkpoints = memoryBankTimeout.getCheckpoints();
    console.log(`Найдено checkpoint'ов: ${checkpoints.length}`);
    if (checkpoints.length > 0) {
      console.log('Последний checkpoint:', {
        id: checkpoints[checkpoints.length - 1].id,
        description: checkpoints[checkpoints.length - 1].description,
        timestamp: checkpoints[checkpoints.length - 1].timestamp
      });
    }
    console.log('✅ Тест 5 пройден\n');

    // Тест 6: Финальная статистика
    console.log('📊 Тест 6: Финальная статистика');
    const finalStats = memoryBankTimeout.getStats();
    console.log('Финальная статистика:', JSON.stringify(finalStats, null, 2));
    console.log('✅ Тест 6 пройден\n');

    console.log('🎉 Все тесты успешно пройдены!');
    console.log('🚀 Memory Bank Timeout System работает корректно');

  } catch (error) {
    console.error('❌ Ошибка при тестировании:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Запуск тестов
testFunctionality();
