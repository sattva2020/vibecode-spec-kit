/**
 * K6 Load Testing Script for RAG-Powered Code Assistant
 * 
 * Тестирует производительность системы под нагрузкой
 * Сценарии: семантический поиск, генерация кода, анализ проектов
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Кастомные метрики
export let errorRate = new Rate('errors');

// Конфигурация теста
export let options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up до 50 пользователей
    { duration: '5m', target: 50 },   // Стабильная нагрузка
    { duration: '2m', target: 100 },  // Ramp up до 100 пользователей
    { duration: '5m', target: 100 },  // Стабильная нагрузка
    { duration: '2m', target: 200 },  // Ramp up до 200 пользователей
    { duration: '5m', target: 200 },  // Пиковая нагрузка
    { duration: '2m', target: 0 },    // Ramp down
  ],
  
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% запросов < 2 сек
    http_req_failed: ['rate<0.1'],     // < 10% ошибок
    errors: ['rate<0.05'],             // < 5% ошибок
  },
};

// Тестовые данные
const testQueries = [
  'authentication middleware',
  'database connection',
  'error handling',
  'API endpoint',
  'user validation',
  'file upload',
  'caching strategy',
  'security headers'
];

const codeSnippets = [
  'function calculateTotal(items) {',
  'class UserService {',
  'const express = require("express");',
  'interface ApiResponse {',
  'async function fetchData(url) {',
  'export const validateUser = (user) => {'
];

// Основная функция теста
export default function() {
  const scenario = Math.random();
  
  if (scenario < 0.4) {
    // 40% - Семантический поиск (Ollama)
    testSemanticSearch();
  } else if (scenario < 0.7) {
    // 30% - Генерация кода (Claude/GPT-4)
    testCodeGeneration();
  } else if (scenario < 0.9) {
    // 20% - Анализ кода (Claude)
    testCodeAnalysis();
  } else {
    // 10% - Создание n8n workflow
    testN8nWorkflow();
  }
  
  sleep(Math.random() * 2 + 1); // 1-3 секунды между запросами
}

/**
 * Тест семантического поиска через Ollama
 */
function testSemanticSearch() {
  const query = testQueries[Math.floor(Math.random() * testQueries.length)];
  
  const payload = JSON.stringify({
    query: query,
    context: 'typescript_project',
    type: 'semantic',
    limit: 10
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.JWT_TOKEN}`
    },
  };
  
  const response = http.post(`${__ENV.BASE_URL}/api/v1/search`, payload, params);
  
  const success = check(response, {
    'semantic search status 200': (r) => r.status === 200,
    'semantic search response time < 2s': (r) => r.timings.duration < 2000,
    'semantic search has results': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.results && body.results.length > 0;
      } catch (e) {
        return false;
      }
    },
    'semantic search provider is ollama': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.provider === 'ollama';
      } catch (e) {
        return false;
      }
    }
  });
  
  errorRate.add(!success);
}

/**
 * Тест генерации кода через Claude/GPT-4
 */
function testCodeGeneration() {
  const snippet = codeSnippets[Math.floor(Math.random() * codeSnippets.length)];
  
  const payload = JSON.stringify({
    task_type: 'code_generation',
    language: 'typescript',
    description: `Complete this code: ${snippet}`,
    complexity: Math.random() > 0.5 ? 'medium' : 'high',
    context: {
      framework: 'express',
      database: 'postgresql',
      testing: 'jest'
    }
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.JWT_TOKEN}`
    },
  };
  
  const response = http.post(`${__ENV.BASE_URL}/api/v1/generate`, payload, params);
  
  const success = check(response, {
    'code generation status 200': (r) => r.status === 200,
    'code generation response time < 5s': (r) => r.timings.duration < 5000,
    'code generation has valid code': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.code && body.code.length > 50;
      } catch (e) {
        return false;
      }
    },
    'code generation provider is claude or openai': (r) => {
      try {
        const body = JSON.parse(r.body);
        return ['claude', 'openai'].includes(body.provider);
      } catch (e) {
        return false;
      }
    }
  });
  
  errorRate.add(!success);
}

/**
 * Тест анализа кода через Claude
 */
function testCodeAnalysis() {
  const codeSample = `
function processUserData(users) {
  return users.map(user => {
    if (user.age > 18) {
      return {
        name: user.name,
        email: user.email,
        status: 'active'
      };
    }
  });
}
  `;
  
  const payload = JSON.stringify({
    task_type: 'code_analysis',
    code: codeSample,
    language: 'javascript',
    analysis_type: 'security_and_performance',
    complexity: 'medium'
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.JWT_TOKEN}`
    },
  };
  
  const response = http.post(`${__ENV.BASE_URL}/api/v1/analyze`, payload, params);
  
  const success = check(response, {
    'code analysis status 200': (r) => r.status === 200,
    'code analysis response time < 3s': (r) => r.timings.duration < 3000,
    'code analysis has suggestions': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.suggestions && body.suggestions.length > 0;
      } catch (e) {
        return false;
      }
    },
    'code analysis provider is claude': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.provider === 'claude';
      } catch (e) {
        return false;
      }
    }
  });
  
  errorRate.add(!success);
}

/**
 * Тест создания n8n workflow
 */
function testN8nWorkflow() {
  const payload = JSON.stringify({
    name: `Test Workflow ${Math.random().toString(36).substr(2, 9)}`,
    description: 'Automated test workflow for code analysis',
    trigger: {
      type: 'webhook',
      path: '/test-webhook'
    },
    nodes: [
      {
        name: 'Webhook',
        type: 'n8n-nodes-base.webhook',
        parameters: {
          path: 'test-webhook',
          httpMethod: 'POST'
        }
      },
      {
        name: 'AI Analysis',
        type: 'n8n-nodes-base.httpRequest',
        parameters: {
          url: 'http://ai-router:8000/api/v1/analyze',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      }
    ],
    connections: {
      'Webhook': {
        'main': [['AI Analysis']]
      }
    }
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-N8N-API-KEY': __ENV.N8N_API_KEY
    },
  };
  
  const response = http.post(`${__ENV.N8N_URL}/api/v1/workflows`, payload, params);
  
  const success = check(response, {
    'n8n workflow creation status 201': (r) => r.status === 201,
    'n8n workflow creation response time < 2s': (r) => r.timings.duration < 2000,
    'n8n workflow has id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.id && body.id.length > 0;
      } catch (e) {
        return false;
      }
    }
  });
  
  errorRate.add(!success);
}

/**
 * Setup функция - выполняется один раз перед тестом
 */
export function setup() {
  console.log('🚀 Настройка нагрузочного тестирования...');
  
  // Проверяем доступность сервисов
  const healthCheck = http.get(`${__ENV.BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Сервис недоступен: ${__ENV.BASE_URL}`);
  }
  
  console.log('✅ Сервисы доступны, начинаем тестирование');
  
  return {
    startTime: new Date().toISOString(),
    baseUrl: __ENV.BASE_URL
  };
}

/**
 * Teardown функция - выполняется один раз после теста
 */
export function teardown(data) {
  console.log('🏁 Завершение нагрузочного тестирования...');
  console.log(`📊 Тест запущен: ${data.startTime}`);
  console.log(`🔗 Base URL: ${data.baseUrl}`);
  console.log('✅ Тестирование завершено');
}
