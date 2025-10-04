/**
 * RAG Service - Main service for interacting with RAG system
 */

import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';

export interface CodeAnalysisRequest {
    code: string;
    language: string;
    filePath: string;
}

export interface CodeAnalysisResponse {
    complexity: number;
    suggestions: Suggestion[];
    patterns: string[];
    metrics: {
        linesOfCode: number;
        cyclomaticComplexity: number;
        maintainabilityIndex: number;
    };
}

export interface Suggestion {
    id: string;
    title: string;
    description: string;
    type: 'insert' | 'replace' | 'refactor';
    code: string;
    position?: vscode.Position;
    range?: vscode.Range;
    confidence: number;
    category: 'performance' | 'security' | 'readability' | 'best-practice';
}

export interface WorkflowRequest {
    code: string;
    analysis: any;
    language: string;
    filePath: string;
}

export interface WorkflowResponse {
    id: string;
    name: string;
    nodes: any[];
    connections: any[];
    metadata: {
        created: string;
        confidence: number;
        complexity: string;
    };
}

export interface HealthStatus {
    status: 'healthy' | 'degraded' | 'error';
    services: {
        ragProxy: boolean;
        ollama: boolean;
        lightrag: boolean;
        n8n: boolean;
    };
    message?: string;
}

export class RAGService {
    private httpClient: AxiosInstance;
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('rag-assistant');
        this.httpClient = axios.create({
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Update configuration when settings change
     */
    updateConfiguration(): void {
        this.config = vscode.workspace.getConfiguration('rag-assistant');
    }

    /**
     * Check health of all RAG system services
     */
    async checkHealth(): Promise<HealthStatus> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');
        const ollamaUrl = this.config.get<string>('ollamaUrl', 'http://localhost:11434');
        const lightragUrl = this.config.get<string>('lightragUrl', 'http://localhost:8001');
        const n8nUrl = this.config.get<string>('n8nUrl', 'http://localhost:5678');

        const services = {
            ragProxy: false,
            ollama: false,
            lightrag: false,
            n8n: false
        };

        let healthyCount = 0;
        const totalServices = Object.keys(services).length;

        // Check RAG Proxy
        try {
            await this.httpClient.get(`${ragProxyUrl}/health`);
            services.ragProxy = true;
            healthyCount++;
        } catch (error) {
            console.warn('RAG Proxy health check failed:', error);
        }

        // Check Ollama
        try {
            await this.httpClient.get(`${ollamaUrl}/api/tags`);
            services.ollama = true;
            healthyCount++;
        } catch (error) {
            console.warn('Ollama health check failed:', error);
        }

        // Check LightRAG
        try {
            await this.httpClient.get(`${lightragUrl}/health`);
            services.lightrag = true;
            healthyCount++;
        } catch (error) {
            console.warn('LightRAG health check failed:', error);
        }

        // Check n8n
        try {
            await this.httpClient.get(`${n8nUrl}/healthz`);
            services.n8n = true;
            healthyCount++;
        } catch (error) {
            console.warn('n8n health check failed:', error);
        }

        let status: 'healthy' | 'degraded' | 'error';
        if (healthyCount === totalServices) {
            status = 'healthy';
        } else if (healthyCount > totalServices / 2) {
            status = 'degraded';
        } else {
            status = 'error';
        }

        return {
            status,
            services,
            message: `${healthyCount}/${totalServices} services healthy`
        };
    }

    /**
     * Analyze code using RAG system
     */
    async analyzeCode(request: CodeAnalysisRequest): Promise<CodeAnalysisResponse> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/analyze`,
                request
            );

            return response.data;
        } catch (error) {
            throw new Error(`Code analysis failed: ${error}`);
        }
    }

    /**
     * Analyze entire project
     */
    async analyzeProject(projectPath: string): Promise<any> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/analyze-project`,
                { projectPath }
            );

            return response.data;
        } catch (error) {
            throw new Error(`Project analysis failed: ${error}`);
        }
    }

    /**
     * Get AI suggestions for current context
     */
    async getSuggestions(context: {
        code: string;
        language: string;
        position: vscode.Position;
        filePath: string;
    }): Promise<Suggestion[]> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');
        const maxSuggestions = this.config.get<number>('maxSuggestions', 5);
        const confidenceThreshold = this.config.get<number>('confidenceThreshold', 0.7);

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/suggestions`,
                {
                    ...context,
                    maxSuggestions,
                    confidenceThreshold
                }
            );

            return response.data.suggestions || [];
        } catch (error) {
            throw new Error(`Failed to get suggestions: ${error}`);
        }
    }

    /**
     * Explain code using AI
     */
    async explainCode(request: CodeAnalysisRequest): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/explain`,
                request
            );

            return response.data.explanation;
        } catch (error) {
            throw new Error(`Code explanation failed: ${error}`);
        }
    }

    /**
     * Optimize code using AI
     */
    async optimizeCode(request: CodeAnalysisRequest): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/optimize`,
                request
            );

            return response.data.optimizedCode;
        } catch (error) {
            throw new Error(`Code optimization failed: ${error}`);
        }
    }

    /**
     * Create n8n workflow from code context
     */
    async createWorkflow(request: WorkflowRequest): Promise<WorkflowResponse> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/create-workflow`,
                request
            );

            return response.data;
        } catch (error) {
            throw new Error(`Workflow creation failed: ${error}`);
        }
    }

    /**
     * Get available Ollama models
     */
    async getAvailableModels(): Promise<string[]> {
        const ollamaUrl = this.config.get<string>('ollamaUrl', 'http://localhost:11434');

        try {
            const response = await this.httpClient.get(`${ollamaUrl}/api/tags`);
            return response.data.models?.map((model: any) => model.name) || [];
        } catch (error) {
            console.warn('Failed to get available models:', error);
            return [];
        }
    }

    /**
     * Get n8n workflows
     */
    async getWorkflows(): Promise<any[]> {
        const n8nUrl = this.config.get<string>('n8nUrl', 'http://localhost:5678');

        try {
            // Note: This would require proper authentication in a real implementation
            const response = await this.httpClient.get(`${n8nUrl}/api/v1/workflows`);
            return response.data || [];
        } catch (error) {
            console.warn('Failed to get workflows:', error);
            return [];
        }
    }

    /**
     * Execute a workflow
     */
    async executeWorkflow(workflowId: string): Promise<any> {
        const n8nUrl = this.config.get<string>('n8nUrl', 'http://localhost:5678');

        try {
            const response = await this.httpClient.post(
                `${n8nUrl}/api/v1/workflows/${workflowId}/execute`
            );

            return response.data;
        } catch (error) {
            throw new Error(`Workflow execution failed: ${error}`);
        }
    }

    /**
     * Get code suggestions for inline completion
     */
    async getCodeSuggestions(context: string): Promise<any[]> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/suggestions`,
                { context }
            );

            return response.data.suggestions || [];
        } catch (error) {
            console.error('Error getting code suggestions:', error);
            return [];
        }
    }

    /**
     * Get code explanation for hover
     */
    async getCodeExplanation(word: string, context: string): Promise<any> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/explain-word`,
                { word, context }
            );

            return response.data;
        } catch (error) {
            console.error('Error getting code explanation:', error);
            return null;
        }
    }

    /**
     * Get function suggestions for code lens
     */
    async getFunctionSuggestions(functionName: string, context: string): Promise<any[]> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/function-suggestions`,
                { functionName, context }
            );

            return response.data.suggestions || [];
        } catch (error) {
            console.error('Error getting function suggestions:', error);
            return [];
        }
    }

    /**
     * Get class improvements for code lens
     */
    async getClassImprovements(className: string, context: string): Promise<any[]> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/class-improvements`,
                { className, context }
            );

            return response.data.improvements || [];
        } catch (error) {
            console.error('Error getting class improvements:', error);
            return [];
        }
    }

    /**
     * Generate documentation
     */
    async generateDocumentation(name: string, context: string): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/generate-docs`,
                { name, context }
            );

            return response.data.documentation || '';
        } catch (error) {
            console.error('Error generating documentation:', error);
            throw error;
        }
    }

    /**
     * Fix code error
     */
    async fixCodeError(code: string, errorMessage: string): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/fix-error`,
                { code, errorMessage }
            );

            return response.data.fixedCode || code;
        } catch (error) {
            console.error('Error fixing code error:', error);
            return code;
        }
    }

    /**
     * Refactor code
     */
    async refactorCode(code: string): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/refactor`,
                { code }
            );

            return response.data.refactoredCode || '';
        } catch (error) {
            console.error('Error refactoring code:', error);
            throw error;
        }
    }

    /**
     * Generate tests
     */
    async generateTests(code: string): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/generate-tests`,
                { code }
            );

            return response.data.testCode || '';
        } catch (error) {
            console.error('Error generating tests:', error);
            throw error;
        }
    }

    /**
     * Generate code from prompt
     */
    async generateCode(prompt: string): Promise<string> {
        const ragProxyUrl = this.config.get<string>('ragProxyUrl', 'http://localhost:8080');

        try {
            const response = await this.httpClient.post(
                `${ragProxyUrl}/api/generate`,
                { prompt }
            );

            return response.data.code || '';
        } catch (error) {
            console.error('Error generating code:', error);
            throw error;
        }
    }
}
