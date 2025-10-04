use crate::config::Config;
use crate::error::RAGProxyError;
use crate::types::*;
use std::collections::HashMap;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LightRAGHealth {
    pub status: String,
    pub service: String,
    pub working_dir: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LightRAGResponse {
    pub result: Option<String>,
    pub suggestions: Option<Vec<CodeSuggestion>>,
    pub error: Option<String>,
}

pub struct RAGService {
    client: Client,
    config: Config,
}

impl RAGService {
    pub async fn new(config: &Config) -> Result<Self, RAGProxyError> {
        let client = Client::builder()
            .timeout(Duration::from_secs(config.rag.timeout_seconds))
            .build()?;

        Ok(Self {
            client,
            config: config.clone(),
        })
    }

    pub async fn health_check(&self) -> Result<LightRAGHealth, RAGProxyError> {
        let url = format!("{}/health", self.config.lightrag.url);
        
        let response = self.client
            .get(&url)
            .send()
            .await?;

        if response.status().is_success() {
            let health: LightRAGHealth = response.json().await?;
            Ok(health)
        } else {
            Err(RAGProxyError::ServiceUnavailable(
                format!("LightRAG health check failed: {}", response.status())
            ))
        }
    }

    pub async fn suggest_code(
        &self,
        request: &CodeContextRequest,
        spec_kit_context: &Option<String>,
    ) -> Result<Vec<CodeSuggestion>, RAGProxyError> {
        let url = format!("{}/suggest", self.config.lightrag.url);
        
        let mut request_body = serde_json::json!({
            "context": request.code,
            "cursor_position": {"line": 0, "character": 0},
            "language": request.language,
            "file_path": request.file_path
        });

        // Add Spec Kit context if available
        if let Some(spec_context) = spec_kit_context {
            request_body["spec_kit_context"] = serde_json::Value::String(spec_context.clone());
        }

        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;

        if response.status().is_success() {
            let result: LightRAGResponse = response.json().await?;
            
            if let Some(suggestions) = result.suggestions {
                // Enhance suggestions with Spec Kit methodology
                let enhanced_suggestions = self.enhance_suggestions_with_spec_kit(
                    suggestions,
                    spec_kit_context,
                    &request.language,
                ).await;
                
                Ok(enhanced_suggestions)
            } else {
                // Fallback suggestions
                Ok(self.generate_fallback_suggestions(&request.language))
            }
        } else {
            Err(RAGProxyError::ServiceError(
                format!("LightRAG suggest failed: {}", response.status())
            ))
        }
    }

    pub async fn search_context(
        &self,
        query: &str,
        spec_kit_context: &Option<String>,
        limit: usize,
    ) -> Result<Vec<SearchResult>, RAGProxyError> {
        let url = format!("{}/query", self.config.lightrag.url);
        
        let mut request_body = serde_json::json!({
            "query": query,
            "mode": "hybrid",
            "top_k": limit
        });

        // Add Spec Kit context for enhanced search
        if let Some(spec_context) = spec_kit_context {
            let enhanced_query = format!("{} [Spec Kit Context: {}]", query, spec_context);
            request_body["query"] = serde_json::Value::String(enhanced_query);
        }

        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;

        if response.status().is_success() {
            let result: serde_json::Value = response.json().await?;
            
            // Parse LightRAG response into SearchResult format
            let mut results = Vec::new();
            
            if let Some(rag_result) = result.get("result").and_then(|r| r.as_str()) {
                // Split result into chunks and create SearchResult objects
                let chunks: Vec<&str> = rag_result.split("\n\n").collect();
                
                for (i, chunk) in chunks.iter().enumerate().take(limit) {
                    if !chunk.trim().is_empty() {
                        results.push(SearchResult {
                            content: chunk.to_string(),
                            relevance: 1.0 - (i as f64 * 0.1), // Decreasing relevance
                            source: "lightrag".to_string(),
                            metadata: HashMap::from([
                                ("spec_kit_enriched".to_string(), spec_kit_context.is_some().to_string()),
                                ("chunk_index".to_string(), i.to_string()),
                            ]),
                        });
                    }
                }
            }
            
            Ok(results)
        } else {
            Err(RAGProxyError::ServiceError(
                format!("LightRAG search failed: {}", response.status())
            ))
        }
    }

    pub async fn learn_from_code(&self, request: &LearnRequest) -> Result<(), RAGProxyError> {
        let url = format!("{}/insert_code", self.config.lightrag.url);
        
        let request_body = serde_json::json!({
            "file_path": request.file_path,
            "code": request.code,
            "language": request.language,
            "context": request.context
        });

        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(RAGProxyError::ServiceError(
                format!("LightRAG learning failed: {}", response.status())
            ))
        }
    }

    pub async fn explain_code(
        &self,
        request: &CodeContextRequest,
        spec_kit_context: &Option<String>,
    ) -> Result<HashMap<String, String>, RAGProxyError> {
        let url = format!("{}/query", self.config.lightrag.url);
        
        let explanation_query = format!("Explain this {} code:\n{}", request.language, request.code);
        
        let mut request_body = serde_json::json!({
            "query": explanation_query,
            "mode": "hybrid",
            "top_k": 5
        });

        // Add Spec Kit context for enhanced explanation
        if let Some(spec_context) = spec_kit_context {
            let enhanced_query = format!("{} [Context: {}]", explanation_query, spec_context);
            request_body["query"] = serde_json::Value::String(enhanced_query);
        }

        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;

        if response.status().is_success() {
            let result: serde_json::Value = response.json().await?;
            
            let mut explanation = HashMap::new();
            
            if let Some(rag_result) = result.get("result").and_then(|r| r.as_str()) {
                explanation.insert("explanation".to_string(), rag_result.to_string());
                explanation.insert("source".to_string(), "lightrag".to_string());
                explanation.insert("spec_kit_enriched".to_string(), spec_kit_context.is_some().to_string());
                
                // Add methodology-specific insights
                if let Some(spec_context) = spec_kit_context {
                    if spec_context.contains("level3") || spec_context.contains("level4") {
                        explanation.insert("methodology".to_string(), "Complex System Architecture".to_string());
                    } else if spec_context.contains("level2") {
                        explanation.insert("methodology".to_string(), "Intermediate Feature Development".to_string());
                    } else {
                        explanation.insert("methodology".to_string(), "Quick Bug Fix / Simple Enhancement".to_string());
                    }
                }
            } else {
                explanation.insert("explanation".to_string(), "No specific explanation available from RAG system.".to_string());
                explanation.insert("source".to_string(), "fallback".to_string());
            }
            
            Ok(explanation)
        } else {
            Err(RAGProxyError::ServiceError(
                format!("LightRAG explanation failed: {}", response.status())
            ))
        }
    }

    async fn enhance_suggestions_with_spec_kit(
        &self,
        mut suggestions: Vec<CodeSuggestion>,
        spec_kit_context: &Option<String>,
        language: &str,
    ) -> Vec<CodeSuggestion> {
        if let Some(spec_context) = spec_kit_context {
            // Add Spec Kit methodology suggestions
            let methodology_suggestion = CodeSuggestion {
                text: self.generate_methodology_suggestion(language, spec_context),
                confidence: 0.9,
                r#type: "methodology".to_string(),
                source: Some("spec_kit".to_string()),
                // Additional fields would go here if needed
            };
            
            suggestions.push(methodology_suggestion);
            
            // Enhance existing suggestions with Spec Kit context
            for _suggestion in &mut suggestions {
                // Enhance suggestions with Spec Kit context if needed
            }
        }
        
        suggestions
    }

    fn generate_methodology_suggestion(&self, language: &str, spec_context: &str) -> String {
        if spec_context.contains("level4") {
            match language {
                "rust" => "// Enterprise-level architecture: Consider implementing trait-based abstractions and comprehensive error handling".to_string(),
                "typescript" => "// Complex system: Implement comprehensive type definitions and architectural patterns".to_string(),
                "python" => "// Enterprise solution: Consider implementing design patterns and comprehensive testing".to_string(),
                _ => "// Complex system implementation: Apply enterprise-level patterns and comprehensive error handling".to_string(),
            }
        } else if spec_context.contains("level3") {
            match language {
                "rust" => "// Intermediate feature: Implement proper error handling and modular design".to_string(),
                "typescript" => "// Component integration: Use proper TypeScript types and modular architecture".to_string(),
                "python" => "// Feature development: Implement proper testing and modular structure".to_string(),
                _ => "// Intermediate development: Apply proper patterns and testing".to_string(),
            }
        } else {
            match language {
                "rust" => "// Quick fix: Implement simple, focused solution".to_string(),
                "typescript" => "// Simple enhancement: Add clear, concise implementation".to_string(),
                "python" => "// Bug fix: Implement straightforward solution".to_string(),
                _ => "// Simple implementation: Focus on clarity and correctness".to_string(),
            }
        }
    }

    fn extract_methodology(&self, spec_context: &str) -> String {
        if spec_context.contains("level4") {
            "Enterprise Solution".to_string()
        } else if spec_context.contains("level3") {
            "Complex System".to_string()
        } else if spec_context.contains("level2") {
            "Intermediate Feature".to_string()
        } else {
            "Quick Fix/Simple Enhancement".to_string()
        }
    }

    fn generate_fallback_suggestions(&self, language: &str) -> Vec<CodeSuggestion> {
        vec![
            CodeSuggestion {
                text: format!("// AI suggestion for {} code", language),
                confidence: 0.7,
                r#type: "completion".to_string(),
                source: Some("fallback".to_string()),
                // Basic suggestion without Spec Kit integration
            },
            CodeSuggestion {
                text: "// Consider adding proper error handling".to_string(),
                confidence: 0.8,
                r#type: "best_practice".to_string(),
                source: Some("spec_kit".to_string()),
                // Quality assurance suggestion
            },
        ]
    }
}
