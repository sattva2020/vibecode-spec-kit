# Phase 2: Integration Testing & Real Service Connection

## 🎯 Overview

Phase 2 focuses on integration testing, real service connections, and performance validation of the Intelligent n8n Workflow Creation System.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with pip
2. **Docker & Docker Compose** (for services)
3. **Git** for version control

### Installation

```bash
# Clone and setup
cd intelligent-n8n-system
pip install -r requirements.txt

# Start Docker services
docker-compose up -d

# Run Phase 2 tests
python scripts/run_phase2.py
```

## 🧪 Test Suite

### Unit Tests
```bash
pytest tests/ -m unit -v
```

### Integration Tests
```bash
pytest tests/ -m integration -v
```

### n8n Integration Tests
```bash
pytest tests/test_n8n_integration.py -v
```

### Model Training Tests
```bash
pytest tests/test_model_training.py -v
```

### Performance Tests
```bash
pytest tests/test_performance.py -v
```

## 🔧 Test Categories

### 1. Pipeline Integration Tests
- **File**: `tests/test_integration_pipeline.py`
- **Purpose**: Test complete AI pipeline execution
- **Coverage**: End-to-end workflow generation

### 2. Service Integration Tests
- **File**: `tests/test_integration_services.py`
- **Purpose**: Test individual service integrations
- **Coverage**: Project analyzer, LightRAG, Decision engine, Workflow generator

### 3. n8n API Integration Tests
- **File**: `tests/test_n8n_integration.py`
- **Purpose**: Test n8n API connectivity and operations
- **Coverage**: CRUD operations, workflow execution, webhooks

### 4. Model Training Tests
- **File**: `tests/test_model_training.py`
- **Purpose**: Test ML model training pipeline
- **Coverage**: Data preparation, model training, evaluation, persistence

### 5. Performance Tests
- **File**: `tests/test_performance.py`
- **Purpose**: Performance and load testing
- **Coverage**: Memory usage, response times, concurrent execution

## 🐳 Docker Services

### Required Services

1. **LightRAG** (Port 8000)
   - Knowledge base service
   - Semantic search capabilities

2. **Supabase** (Port 54321)
   - PostgreSQL database with pgvector
   - Real-time capabilities

3. **n8n** (Port 5678)
   - Workflow automation platform
   - API for workflow management

4. **Ollama** (Port 11434)
   - Local LLM runtime
   - Models: llama3.2, nomic-embed-text

### Service Health Checks

```bash
# Check all services
curl http://localhost:8000/health  # LightRAG
curl http://localhost:54321/health # Supabase
curl http://localhost:5678/healthz # n8n
curl http://localhost:11434/api/tags # Ollama
```

## 📊 Performance Benchmarks

### Expected Performance Metrics

| Test Type | Target Time | Max Memory | Success Rate |
|-----------|-------------|------------|--------------|
| Project Analysis | < 30s | < 500MB | 95%+ |
| Pipeline Execution | < 60s | < 1GB | 90%+ |
| API Response | < 5s | < 100MB | 95%+ |
| Concurrent Load | < 120s | < 2GB | 80%+ |

### Performance Monitoring

```bash
# Run performance benchmarks
pytest tests/test_performance.py -v --benchmark-only

# Monitor memory usage
python -m pytest tests/test_performance.py::TestPerformance::test_memory_usage_under_load -v
```

## 🔍 Integration Test Scenarios

### Scenario 1: Complete Pipeline Execution
```python
# Test end-to-end workflow generation
async def test_complete_pipeline():
    coordinator = PipelineCoordinator()
    result = await coordinator.execute_pipeline(
        project_path="test_project",
        request_id="test-123"
    )
    assert result.success
    assert len(result.workflows) > 0
```

### Scenario 2: n8n Workflow CRUD
```python
# Test n8n API operations
async def test_n8n_workflow_crud():
    client = N8nClient()
    workflow = await client.create_workflow(test_workflow)
    assert workflow["id"] is not None
    
    workflows = await client.get_workflows()
    assert len(workflows) > 0
```

### Scenario 3: Model Training Pipeline
```python
# Test ML model training
async def test_model_training():
    pipeline = TrainingPipeline()
    results = await pipeline.train_models(training_data)
    assert results["random_forest"]["accuracy"] > 0.8
```

## 🚨 Troubleshooting

### Common Issues

1. **Docker Services Not Running**
   ```bash
   # Check Docker status
   docker ps
   
   # Restart services
   docker-compose down && docker-compose up -d
   ```

2. **Test Failures**
   ```bash
   # Run with verbose output
   pytest tests/ -v --tb=long
   
   # Run specific test
   pytest tests/test_integration_pipeline.py::TestPipelineIntegration::test_complete_pipeline_execution -v
   ```

3. **Memory Issues**
   ```bash
   # Run with memory profiling
   pytest tests/test_performance.py --profile
   
   # Check system resources
   python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
   ```

4. **API Connection Issues**
   ```bash
   # Test service connectivity
   python -c "
   import httpx
   import asyncio
   
   async def test_services():
       services = ['http://localhost:8000', 'http://localhost:54321', 'http://localhost:5678']
       async with httpx.AsyncClient() as client:
           for url in services:
               try:
                   response = await client.get(f'{url}/health')
                   print(f'{url}: {response.status_code}')
               except Exception as e:
                   print(f'{url}: ERROR - {e}')
   
   asyncio.run(test_services())
   "
   ```

## 📈 Success Criteria

### Phase 2 Completion Requirements

- [ ] **Unit Tests**: 95%+ pass rate
- [ ] **Integration Tests**: 90%+ pass rate
- [ ] **n8n Integration**: All CRUD operations working
- [ ] **Model Training**: Models train successfully
- [ ] **Performance**: All benchmarks meet targets
- [ ] **API Testing**: All endpoints responding correctly

### Quality Gates

1. **Code Coverage**: > 80%
2. **Performance**: All benchmarks pass
3. **Integration**: All services connected
4. **Documentation**: All APIs documented

## 🎯 Next Steps

After successful Phase 2 completion:

1. **Phase 3**: Integration & Learning
   - Feedback learning system
   - Continuous improvement
   - Production deployment

2. **Phase 4**: Production Ready
   - Monitoring & alerting
   - Documentation
   - User training

## 📚 Additional Resources

- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Performance Tuning](docs/performance.md)

## 🤝 Contributing

1. Run tests before committing
2. Follow code style guidelines
3. Update documentation
4. Add tests for new features

```bash
# Pre-commit checks
pre-commit run --all-files

# Run full test suite
python scripts/run_phase2.py --performance
```
