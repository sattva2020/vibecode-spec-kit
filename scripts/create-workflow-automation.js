// Автоматизация создания n8n workflow через Playwright
// ======================================================

const { chromium } = require('playwright');

async function createN8NWorkflow() {
    console.log('🚀 Запуск автоматизации создания n8n workflow...');
    
    const browser = await chromium.launch({ 
        headless: false, // Показываем браузер для отладки
        slowMo: 1000 // Замедляем для наблюдения
    });
    
    try {
        const page = await browser.newPage();
        
        // Переходим на n8n
        console.log('📋 Открываем n8n...');
        await page.goto('http://localhost:8080');
        
        // Ждем загрузки страницы
        await page.waitForSelector('body', { timeout: 10000 });
        
        // Проверяем нужна ли авторизация
        const loginForm = await page.$('input[type="password"]');
        if (loginForm) {
            console.log('🔑 Выполняем авторизацию...');
            await page.fill('input[type="text"]', 'admin');
            await page.fill('input[type="password"]', 'password');
            await page.click('button[type="submit"]');
            await page.waitForNavigation();
        }
        
        // Создаем новый workflow
        console.log('➕ Создаем новый workflow...');
        await page.click('button:has-text("New workflow")');
        
        // Ждем загрузки редактора
        await page.waitForSelector('.node-creator', { timeout: 10000 });
        
        console.log('✅ n8n готов к созданию workflow!');
        console.log('📝 Следующие шаги выполняйте вручную:');
        console.log('1. Добавьте узел "Webhook"');
        console.log('2. Добавьте узел "HTTP Request" для Ollama');
        console.log('3. Добавьте узел "HTTP Request" для Supabase');
        console.log('4. Соедините узлы');
        console.log('5. Активируйте workflow');
        
        // Оставляем браузер открытым для ручной настройки
        console.log('🌐 Браузер остается открытым для ручной настройки...');
        console.log('Нажмите Enter когда закончите...');
        
        // Ждем нажатия Enter
        await new Promise(resolve => {
            process.stdin.once('data', () => resolve());
        });
        
    } catch (error) {
        console.error('❌ Ошибка:', error.message);
    } finally {
        await browser.close();
    }
}

// Запускаем автоматизацию
createN8NWorkflow().catch(console.error);
