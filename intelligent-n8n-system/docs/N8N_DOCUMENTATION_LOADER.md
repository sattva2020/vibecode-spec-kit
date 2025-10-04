# N8N Documentation Loader

## Overview

The N8N Documentation Loader is a comprehensive system for automatically loading and processing n8n documentation from various sources into the LightRAG knowledge base. This enables the intelligent n8n workflow creation system to have access to up-to-date n8n documentation for better workflow suggestions.

## Features

- **Multi-source documentation loading**: Supports web documentation, GitHub repositories, and API documentation
- **Intelligent caching**: Caches documentation locally to avoid repeated downloads
- **Automatic updates**: Configurable update intervals to keep documentation fresh
- **Content processing**: Converts HTML to Markdown and cleans content for better processing
- **LightRAG integration**: Seamlessly integrates with LightRAG for knowledge base indexing

## Documentation Sources

The system loads documentation from the following sources:

1. **Official n8n Documentation** (`https://docs.n8n.io`)
   - Complete n8n documentation
   - Node references and guides
   - API documentation
   - Tutorials and examples

2. **n8n Nodes Base Repository** (`https://github.com/n8n-io/n8n-nodes-base`)
   - Source code for core n8n nodes
   - Node documentation and examples
   - Implementation details

3. **n8n Community Nodes Repository** (`https://github.com/n8n-io/n8n-nodes-community`)
   - Community-contributed nodes
   - Extended functionality documentation
   - Community examples

4. **n8n API Documentation** (`https://docs.n8n.io/api`)
   - REST API reference
   - Webhook documentation
   - Integration examples

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```bash
# N8N Documentation Sources
N8N_DOCS_URL=https://docs.n8n.io
N8N_NODES_REPO=https://github.com/n8n-io/n8n-nodes-base
N8N_COMMUNITY_NODES_REPO=https://github.com/n8n-io/n8n-nodes-community
N8N_API_DOCS_URL=https://docs.n8n.io/api

# Documentation Cache
DOCS_CACHE_DIR=./data/documentation
DOCS_UPDATE_INTERVAL_HOURS=24
```

### Configuration Options

- `N8N_DOCS_URL`: Main n8n documentation URL
- `N8N_NODES_REPO`: GitHub repository for core n8n nodes
- `N8N_COMMUNITY_NODES_REPO`: GitHub repository for community nodes
- `N8N_API_DOCS_URL`: n8n API documentation URL
- `DOCS_CACHE_DIR`: Directory to store cached documentation
- `DOCS_UPDATE_INTERVAL_HOURS`: How often to check for updates (default: 24 hours)

## Usage

### Command Line Interface

The documentation loader can be used via the CLI script:

```bash
# Load documentation without indexing to LightRAG
python scripts/load_n8n_docs.py --load-only

# Load documentation and index into LightRAG
python scripts/load_n8n_docs.py --load-and-index

# List available documentation sources
python scripts/load_n8n_docs.py --list-sources

# Check cache status
python scripts/load_n8n_docs.py --check-cache

# Force update all documentation sources
python scripts/load_n8n_docs.py --force-update

# Enable verbose logging
python scripts/load_n8n_docs.py --load-and-index --verbose
```

### Programmatic Usage

```python
from src.knowledge.documentation_loader import N8nDocumentationLoader

async def load_docs():
    async with N8nDocumentationLoader() as loader:
        # Load all documentation
        results = await loader.load_all_documentation()
        
        # Get documents ready for ingestion
        documents = await loader.get_documentation_for_ingestion()
        
        print(f"Loaded {len(documents)} documents")

# Run the loader
import asyncio
asyncio.run(load_docs())
```

### Integration with LightRAG Service

The documentation loader is automatically integrated with the LightRAG service:

```python
from src.knowledge.lightrag_service import LightRAGService

async def initialize_knowledge_base():
    service = LightRAGService()
    
    # This will automatically load and index n8n documentation
    success = await service.initialize_knowledge_base()
    
    if success:
        print("Knowledge base initialized with n8n documentation")
```

## Architecture

### DocumentationLoader Class

The main class that handles loading documentation from various sources:

```python
class N8nDocumentationLoader:
    def __init__(self):
        # Initialize configuration and sources
        
    async def load_all_documentation(self) -> Dict[str, Any]:
        # Load from all configured sources
        
    async def get_documentation_for_ingestion(self) -> List[Dict[str, Any]]:
        # Get cached documentation ready for LightRAG ingestion
```

### Source Types

1. **Web Sources**: HTML documentation that gets converted to Markdown
2. **GitHub Sources**: Repository documentation including README files and node docs

### Caching Strategy

- Documentation is cached locally in JSON format
- Cache files include metadata (last updated, document count, etc.)
- Automatic cache invalidation based on update intervals
- Cache can be manually cleared for force updates

## Content Processing

### HTML to Markdown Conversion

Web documentation is processed as follows:

1. **HTML Parsing**: Uses BeautifulSoup to parse HTML content
2. **Content Extraction**: Identifies main content areas using CSS selectors
3. **Markdown Conversion**: Converts HTML to Markdown using markdownify
4. **Content Cleaning**: Removes web artifacts and excessive whitespace

### GitHub Content Processing

GitHub repositories are processed as follows:

1. **API Access**: Uses GitHub API to fetch repository contents
2. **README Processing**: Extracts and processes README files
3. **Node Documentation**: Loads documentation from individual node directories
4. **File Filtering**: Only processes relevant files (.md, .txt, .json)

## Error Handling

The system includes comprehensive error handling:

- **Network Errors**: Retries and graceful fallbacks
- **Parsing Errors**: Skips problematic content with warnings
- **Cache Errors**: Falls back to fresh downloads
- **API Rate Limits**: Respects GitHub API limits

## Monitoring and Logging

The system provides detailed logging:

- **Load Progress**: Real-time progress updates
- **Error Reporting**: Detailed error messages with context
- **Performance Metrics**: Load times and document counts
- **Cache Status**: Information about cached vs fresh content

## Performance Considerations

### Optimization Strategies

1. **Parallel Loading**: Loads from multiple sources concurrently
2. **Content Filtering**: Skips very short or irrelevant content
3. **Incremental Updates**: Only updates changed content
4. **Efficient Caching**: Reduces redundant downloads

### Resource Usage

- **Memory**: Caches documentation in memory during processing
- **Disk**: Stores cached documentation locally
- **Network**: Downloads documentation from various sources
- **CPU**: Processes HTML and converts to Markdown

## Troubleshooting

### Common Issues

1. **Network Connectivity**: Ensure internet access for downloading documentation
2. **GitHub API Limits**: May need to wait or use authentication for large repositories
3. **Cache Corruption**: Clear cache directory and reload documentation
4. **Memory Issues**: Large documentation sets may require more memory

### Debug Mode

Enable verbose logging to see detailed information:

```bash
python scripts/load_n8n_docs.py --load-and-index --verbose
```

### Cache Management

```bash
# Check cache status
python scripts/load_n8n_docs.py --check-cache

# Force update (clears cache)
python scripts/load_n8n_docs.py --force-update
```

## Future Enhancements

Planned improvements include:

1. **Additional Sources**: Support for more documentation sources
2. **Content Filtering**: More sophisticated content relevance filtering
3. **Incremental Updates**: Better change detection for updates
4. **Performance Optimization**: Faster loading and processing
5. **Custom Sources**: Support for user-defined documentation sources

## Contributing

To contribute to the documentation loader:

1. Add new source types in `DocumentationSource`
2. Implement new loading methods in `N8nDocumentationLoader`
3. Add tests for new functionality
4. Update documentation and examples

## License

This documentation loader is part of the Intelligent n8n Workflow Creation System and follows the same license terms.
