# Intelligent n8n Workflow Creation System

AI-powered system for automatically creating n8n workflows based on project analysis and context understanding.

## 🎯 Overview

This system analyzes your project structure, technologies, and patterns to intelligently generate n8n workflows that can automate various aspects of your development and deployment processes.

## 🏗️ Architecture

The system uses a **Hybrid Pipeline Architecture** with the following components:

### Core Components

1. **Project Context Analyzer** - Analyzes project structure, technologies, and patterns
2. **LightRAG Knowledge Service** - Provides semantic search and n8n knowledge
3. **Ensemble Decision Engine** - Combines multiple ML models for intelligent decisions
4. **Workflow Generator** - Creates actual n8n workflows based on decisions
5. **Pipeline Coordinator** - Orchestrates the entire process

### ML Models

- **Random Forest** - For structured data analysis
- **Neural Network** - For semantic understanding
- **Rule-Based** - For business logic decisions
- **SVM** - For pattern recognition

## 🚀 Features

- **Intelligent Project Analysis** - Understands your project structure and technologies
- **Semantic Knowledge Search** - Finds relevant n8n nodes and patterns
- **Ensemble Decision Making** - Combines multiple AI models for better decisions
- **Automated Workflow Generation** - Creates complete n8n workflows
- **REST API** - Easy integration with other tools
- **Real-time Status** - Monitor pipeline execution

## 📋 Prerequisites

- Python 3.8+
- LightRAG service running
- Supabase instance
- n8n instance
- Ollama (for local LLMs)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intelligent-n8n-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Setup directories**
   ```bash
   python -c "from src.core.config import setup_directories; setup_directories()"
   ```

## 🔧 Configuration

Edit the `.env` file with your configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# LightRAG Configuration
LIGHTRAG_URL=http://localhost:8000
LIGHTRAG_WORKSPACE=/workspace/lightrag

# Supabase Configuration
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_supabase_anon_key

# n8n Configuration
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=admin123

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_CODE=llama3.2:3b
OLLAMA_MODEL_EMBEDDING=nomic-embed-text:latest
```

## 🚀 Usage

### Starting the System

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### Example Usage

#### 1. Analyze a Project

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/your/project",
    "user_id": "user123"
  }'
```

#### 2. Generate Workflows

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/your/project",
    "user_id": "user123",
    "preferences": {
      "workflow_types": ["api_integration", "monitoring"]
    }
  }'
```

#### 3. Check System Status

```bash
curl "http://localhost:8000/status"
```

## 📊 Supported Workflow Types

The system can generate workflows for:

- **API Integration** - Connect and monitor APIs
- **Database Management** - Backup, migration, and monitoring
- **Container Automation** - Build and deployment pipelines
- **Testing Automation** - Automated testing workflows
- **Monitoring** - Health checks and alerts
- **Data Processing** - ETL and transformation pipelines

## 🧠 How It Works

1. **Project Analysis** - Analyzes your project structure, technologies, and patterns
2. **Knowledge Query** - Searches the n8n knowledge base for relevant information
3. **Decision Making** - Uses ensemble ML models to decide what workflows to create
4. **Workflow Generation** - Creates complete n8n workflows with nodes and connections
5. **Validation** - Validates the generated workflows

## 📁 Project Structure

```
intelligent-n8n-system/
├── src/
│   ├── core/                 # Core configuration and pipeline coordinator
│   ├── analyzers/           # Project analysis components
│   ├── knowledge/           # LightRAG integration
│   ├── decision/            # ML decision engine
│   ├── generator/           # Workflow generation
│   └── api/                 # FastAPI application
├── tests/                   # Test files
├── docs/                    # Documentation
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔍 API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `GET /status` - System status
- `POST /api/analyze` - Analyze a project
- `POST /api/generate` - Generate workflows
- `GET /api/pipeline/status/{request_id}` - Pipeline status
- `GET /api/workflows` - List workflow templates
- `POST /api/workflows/validate` - Validate workflow
- `GET /api/knowledge/nodes` - Available nodes
- `GET /api/knowledge/nodes/{node_name}` - Node details

## 🧪 Testing

Run tests with:

```bash
pytest tests/
```

## 📈 Monitoring

The system provides:

- **Pipeline Status** - Real-time execution status
- **Generation Statistics** - Success rates and performance metrics
- **Health Checks** - Component health monitoring
- **Logging** - Comprehensive logging for debugging

## 🔧 Development

### Adding New Node Types

1. Add node template to `WorkflowGenerator.node_templates`
2. Add parameter customization logic
3. Update workflow patterns

### Adding New ML Models

1. Create new model class inheriting from base model
2. Add to ensemble in `EnsembleDecisionEngine`
3. Update model weights and training logic

### Extending Knowledge Base

1. Add new knowledge sources to `LightRAGService`
2. Update indexing logic
3. Add semantic search patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the API docs at `/docs`

## 🔮 Roadmap

- [ ] Advanced workflow optimization
- [ ] Integration with more CI/CD tools
- [ ] Custom model training interface
- [ ] Workflow performance analytics
- [ ] Multi-language support
- [ ] Cloud deployment options
