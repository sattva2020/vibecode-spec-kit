const axios = require('axios');

class RAGClient {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 10000,
        });
    }

    async searchContext(query, options = {}) {
        try {
            const response = await this.client.post('/context/search', {
                query,
                top_k: options.topK || 5,
                mode: options.mode || 'hybrid'
            });
            return response.data;
        } catch (error) {
            console.error('RAG search error:', error);
            throw error;
        }
    }

    async indexContent(text, source, metadata = {}) {
        try {
            await this.client.post('/context/index', {
                text,
                source,
                metadata
            });
            return true;
        } catch (error) {
            console.error('RAG index error:', error);
            throw error;
        }
    }

    async getExamples(topic, limit = 3) {
        try {
            const response = await this.client.post('/context/examples', {
                topic,
                limit
            });
            return response.data.examples;
        } catch (error) {
            console.error('RAG examples error:', error);
            throw error;
        }
    }

    async triggerWorkflow(workflowId, payload) {
        try {
            const response = await this.client.post('/task/automate', {
                workflow_id: workflowId,
                payload
            });
            return response.data;
        } catch (error) {
            console.error('n8n trigger error:', error);
            throw error;
        }
    }

    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            return { status: 'unhealthy', error: error.message };
        }
    }
}

module.exports = RAGClient;
