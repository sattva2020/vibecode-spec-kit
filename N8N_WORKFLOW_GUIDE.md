# 🚀 Руководство по созданию n8n Workflow для генерации кода

## 📋 **Пошаговое создание workflow:**

### **Шаг 1: Откройте n8n**
- Перейдите по адресу: http://localhost:8080
- Создайте аккаунт или войдите в систему

### **Шаг 2: Создайте новый workflow**
1. Нажмите **"New workflow"**
2. Назовите workflow: **"Code Generation with Ollama"**

### **Шаг 3: Добавьте узлы**

#### **Узел 1: Webhook**
1. Перетащите узел **"Webhook"** на canvas
2. Настройте:
   - **Path**: `generate-code`
   - **HTTP Method**: `POST`
   - **Response Mode**: `On Received`

#### **Узел 2: HTTP Request (Ollama)**
1. Перетащите узел **"HTTP Request"** на canvas
2. Настройте:
   - **URL**: `http://rag-ollama:11434/api/generate`
   - **Method**: `POST`
   - **Headers**:
     - `Content-Type: application/json`
   - **Body** (JSON):
     ```json
     {
       "model": "qwen2.5-coder:1.5b",
       "prompt": "={{ $json.prompt }}",
       "stream": false
     }
     ```

#### **Узел 3: HTTP Request (Supabase)**
1. Перетащите узел **"HTTP Request"** на canvas
2. Настройте:
   - **URL**: `http://rag-supabase-db:5432/rest/v1/generated_code`
   - **Method**: `POST`
   - **Headers**:
     - `Content-Type: application/json`
     - `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0`
   - **Body** (JSON):
     ```json
     {
       "code": "={{ $json.response }}",
       "language": "python",
       "prompt": "={{ $('Webhook').item.json.prompt }}"
     }
     ```

#### **Узел 4: Response**
1. Перетащите узел **"Respond to Webhook"** на canvas
2. Настройте:
   - **Response Body** (JSON):
     ```json
     {
       "code": "={{ $('HTTP Request').item.json.response }}",
       "status": "success",
       "saved_to_db": "yes"
     }
     ```

### **Шаг 4: Соедините узлы**
1. **Webhook** → **HTTP Request (Ollama)**
2. **HTTP Request (Ollama)** → **HTTP Request (Supabase)**
3. **HTTP Request (Supabase)** → **Respond to Webhook**

### **Шаг 5: Активируйте workflow**
1. Нажмите **"Active"** в правом верхнем углу
2. Workflow должен стать зеленым

### **Шаг 6: Протестируйте workflow**

#### **Тест через curl:**
```bash
curl -X POST http://localhost:8080/webhook/generate-code \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a Python function to calculate fibonacci"}'
```

#### **Тест через PowerShell:**
```powershell
$body = @{
    prompt = "Write a Python function to calculate fibonacci"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/webhook/generate-code" -Method POST -Body $body -ContentType "application/json"
```

## 🎯 **Ожидаемый результат:**

```json
{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "status": "success",
  "saved_to_db": "yes"
}
```

## 🔧 **Устранение неполадок:**

### **Если Ollama недоступен:**
- Проверьте: `docker ps | findstr ollama`
- Перезапустите: `docker-compose restart rag-ollama`

### **Если Supabase недоступен:**
- Проверьте: `docker ps | findstr supabase`
- Перезапустите: `docker-compose restart rag-supabase-db`

### **Если webhook не работает:**
- Убедитесь что workflow активирован
- Проверьте URL webhook в n8n интерфейсе
- Проверьте логи n8n: `docker logs rag-n8n`

## 🚀 **Дополнительные возможности:**

### **Добавить обработку ошибок:**
1. Добавьте узел **"IF"** после Ollama
2. Проверьте статус ответа
3. Добавьте разные пути для успеха/ошибки

### **Добавить валидацию:**
1. Добавьте узел **"Function"** после Webhook
2. Проверьте наличие поля `prompt`
3. Валидируйте длину prompt

### **Добавить логирование:**
1. Добавьте узел **"Function"** для логирования
2. Сохраняйте timestamp и статус выполнения

## ✅ **Готово!**

Ваш n8n workflow готов к использованию для автоматической генерации кода с помощью Ollama!
