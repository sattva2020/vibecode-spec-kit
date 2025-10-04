// use crate::config::Config; // Unused for now
use crate::error::RAGProxyError;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use tokio::fs;
use tokio::io::AsyncWriteExt;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct MemoryBankStatus {
    pub initialized: bool,
    pub current_mode: String,
    pub issues: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryBankContext {
    pub current_mode: String,
    pub active_context: HashMap<String, String>,
    pub last_updated: String,
}

pub struct MemoryBankClient {
    memory_bank_path: PathBuf,
}

impl MemoryBankClient {
    pub fn new(memory_bank_path: &str) -> Result<Self, RAGProxyError> {
        let path = PathBuf::from(memory_bank_path);
        Ok(Self {
            memory_bank_path: path,
        })
    }

    pub async fn is_initialized(&self) -> Result<bool, RAGProxyError> {
        let essential_files = ["tasks.md", "activeContext.md", "progress.md"];
        
        for file in essential_files.iter() {
            let file_path = self.memory_bank_path.join(file);
            if !file_path.exists() {
                return Ok(false);
            }
        }
        
        Ok(true)
    }

    pub async fn initialize(&self) -> Result<(), RAGProxyError> {
        // Create main directory
        fs::create_dir_all(&self.memory_bank_path).await?;
        
        // Create subdirectories
        let subdirs = ["creative", "reflection", "archive"];
        for subdir in subdirs.iter() {
            let subdir_path = self.memory_bank_path.join(subdir);
            fs::create_dir_all(&subdir_path).await?;
        }
        
        // Create essential files
        self.create_essential_files().await?;
        
        Ok(())
    }

    async fn create_essential_files(&self) -> Result<(), RAGProxyError> {
        // Create tasks.md
        let tasks_file = self.memory_bank_path.join("tasks.md");
        if !tasks_file.exists() {
            let tasks_content = self.get_tasks_template();
            fs::write(&tasks_file, tasks_content).await?;
        }
        
        // Create activeContext.md
        let context_file = self.memory_bank_path.join("activeContext.md");
        if !context_file.exists() {
            let context_content = self.get_context_template();
            fs::write(&context_file, context_content).await?;
        }
        
        // Create progress.md
        let progress_file = self.memory_bank_path.join("progress.md");
        if !progress_file.exists() {
            let progress_content = self.get_progress_template();
            fs::write(&progress_file, progress_content).await?;
        }
        
        Ok(())
    }

    pub async fn get_status(&self) -> Result<MemoryBankStatus, RAGProxyError> {
        let mut issues = Vec::new();
        let mut initialized = true;
        
        // Check essential files
        let essential_files = ["tasks.md", "activeContext.md", "progress.md"];
        for file in essential_files.iter() {
            let file_path = self.memory_bank_path.join(file);
            if !file_path.exists() {
                issues.push(format!("Missing essential file: {}", file));
                initialized = false;
            }
        }
        
        // Check subdirectories
        let subdirs = ["creative", "reflection", "archive"];
        for subdir in subdirs.iter() {
            let subdir_path = self.memory_bank_path.join(subdir);
            if !subdir_path.exists() {
                issues.push(format!("Missing subdirectory: {}", subdir));
                initialized = false;
            }
        }
        
        // Get current mode
        let current_mode = self.get_current_mode().await.unwrap_or_else(|_| "unknown".to_string());
        
        Ok(MemoryBankStatus {
            initialized,
            current_mode,
            issues,
        })
    }

    pub async fn get_context(&self) -> Result<HashMap<String, String>, RAGProxyError> {
        let context_file = self.memory_bank_path.join("activeContext.md");
        
        if !context_file.exists() {
            return Ok(HashMap::from([
                ("current_mode".to_string(), "unknown".to_string()),
            ]));
        }
        
        let content = fs::read_to_string(&context_file).await?;
        let mut context = HashMap::new();
        
        // Parse activeContext.md for current context
        for line in content.lines() {
            if line.starts_with("**Mode**:") {
                let mode_part = line.split("**Mode**:").nth(1).unwrap_or("").trim();
                context.insert("current_mode".to_string(), mode_part.split_whitespace().next().unwrap_or("unknown").to_lowercase());
            } else if line.starts_with("**Session**:") {
                let session_part = line.split("**Session**:").nth(1).unwrap_or("").trim();
                context.insert("current_session".to_string(), session_part.to_string());
            } else if line.starts_with("**Current Focus**:") {
                let focus_part = line.split("**Current Focus**:").nth(1).unwrap_or("").trim();
                context.insert("current_focus".to_string(), focus_part.to_string());
            }
        }
        
        if !context.contains_key("current_mode") {
            context.insert("current_mode".to_string(), "unknown".to_string());
        }
        
        Ok(context)
    }

    pub async fn update_context(&self, context_data: HashMap<String, serde_json::Value>) -> Result<(), RAGProxyError> {
        let context_file = self.memory_bank_path.join("activeContext.md");
        
        // Read existing context
        let existing_content = if context_file.exists() {
            fs::read_to_string(&context_file).await?
        } else {
            self.get_context_template()
        };
        
        let mut updated_content = existing_content;
        
        // Update context information
        for (key, value) in context_data {
            if let Some(str_value) = value.as_str() {
                match key.as_str() {
                    "current_mode" => {
                        updated_content = self.update_context_field(&updated_content, "**Mode**:", &str_value.to_uppercase());
                    }
                    "current_session" => {
                        updated_content = self.update_context_field(&updated_content, "**Session**:", str_value);
                    }
                    "current_focus" => {
                        updated_content = self.update_context_field(&updated_content, "**Current Focus**:", str_value);
                    }
                    _ => {
                        // Add new fields
                        updated_content.push_str(&format!("\n**{}**: {}", key, str_value));
                    }
                }
            }
        }
        
        // Write updated content
        fs::write(&context_file, updated_content).await?;
        
        Ok(())
    }

    fn update_context_field(&self, content: &str, field: &str, value: &str) -> String {
        if content.contains(field) {
            // Update existing field
            content.lines()
                .map(|line| {
                    if line.starts_with(field) {
                        format!("{} {}", field, value)
                    } else {
                        line.to_string()
                    }
                })
                .collect::<Vec<_>>()
                .join("\n")
        } else {
            // Add new field
            format!("{}\n{} {}", content, field, value)
        }
    }

    pub async fn get_current_mode(&self) -> Result<String, RAGProxyError> {
        let context = self.get_context().await?;
        Ok(context.get("current_mode").cloned().unwrap_or_else(|| "unknown".to_string()))
    }

    pub async fn integrate_rag_context(&self, spec_type: &str, code: &str) -> Result<String, RAGProxyError> {
        // Get current context
        let context = self.get_context().await?;
        
        // Create RAG context based on Spec Kit methodology
        let rag_context = format!(
            "Vibecode Spec Kit Context:\n- Current Mode: {}\n- Spec Type: {}\n- Memory Bank Status: {}\n\nCode Context:\n{}\n\nIntegration Points:\n- Spec-driven development methodology\n- Memory-first principle\n- Constitutional AI approach",
            context.get("current_mode").unwrap_or(&"unknown".to_string()),
            spec_type,
            self.get_status().await.map(|s| s.initialized).unwrap_or(false),
            code
        );
        
        // Store in memory bank for future reference
        let rag_file = self.memory_bank_path.join("rag_context.md");
        let mut file = fs::OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&rag_file)
            .await?;
        
        let content = format!("# RAG Integration Context\n\n{}", rag_context);
        file.write_all(content.as_bytes()).await?;
        
        Ok("Memory Bank integrated with RAG context".to_string())
    }

    pub async fn get_rag_context(&self, query: &str) -> Result<Option<String>, RAGProxyError> {
        // Read RAG context file
        let rag_file = self.memory_bank_path.join("rag_context.md");
        
        if rag_file.exists() {
            let content = fs::read_to_string(&rag_file).await?;
            
            // Simple query matching (could be enhanced with semantic search)
            if content.to_lowercase().contains(&query.to_lowercase()) {
                return Ok(Some(content));
            }
        }
        
        // Fallback to activeContext.md
        let context_file = self.memory_bank_path.join("activeContext.md");
        if context_file.exists() {
            let content = fs::read_to_string(&context_file).await?;
            return Ok(Some(content));
        }
        
        Ok(None)
    }

    pub async fn health_check(&self) -> Result<MemoryBankStatus, RAGProxyError> {
        self.get_status().await
    }

    fn get_tasks_template(&self) -> String {
        r#"# Memory Bank Tasks

**Status**: ACTIVE  
**Last Updated**: [DATE]  
**Current Phase**: [PHASE]

## Current Task
- **Task**: [Task Description]
- **Complexity Level**: [1/2/3/4]
- **Status**: [Status]

## Task Queue
- [ ] [Task 1]
- [ ] [Task 2]

## Notes
- [Note 1]
- [Note 2]
"#.to_string()
    }

    fn get_context_template(&self) -> String {
        r#"# Active Context

**Session**: [Session Name]  
**Date**: [DATE]  
**Current Focus**: [Focus Area]

## Current Context
- **Mode**: [Current Mode]
- **Platform**: [Platform]
- **Location**: [Location]
- **Status**: [Status]

## Recent Decisions
- [Decision 1]
- [Decision 2]

## Next Steps
- [Step 1]
- [Step 2]
"#.to_string()
    }

    fn get_progress_template(&self) -> String {
        r#"# Progress Tracking

**Project**: [Project Name]  
**Start Date**: [DATE]  
**Current Phase**: [Current Phase]

## Phase Status
- [ ] [Phase 1]
- [ ] [Phase 2]

## Completed Tasks
1. **[Task 1]**: [Description]
2. **[Task 2]**: [Description]

## Current Task
- **Task**: [Current Task]
- **Status**: [Status]
- **Next**: [Next Step]

## Metrics
- **Files Created**: [Count]
- **Directories Created**: [Count]
- **Time Elapsed**: [Duration]
"#.to_string()
    }
}
