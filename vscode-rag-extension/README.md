# RAG-Powered Code Assistant Extension

AI-powered VS Code extension that provides intelligent code assistance using a RAG (Retrieval-Augmented Generation) system with Ollama, LightRAG, and n8n integration.

## Features

### 🤖 AI-Powered Code Assistance
- **Inline Completions**: Get AI-powered code suggestions as you type
- **Hover Explanations**: Hover over code elements to get AI explanations
- **Code Lens**: See AI suggestions and improvements directly in your code
- **Code Analysis**: Analyze code complexity, patterns, and quality metrics

### 🛠️ Quick Actions
- **Analyze Selection**: Analyze selected code for improvements
- **Generate from Comment**: Generate code from TODO/FIXME comments
- **Optimize Code**: AI-powered code optimization
- **Add Documentation**: Auto-generate documentation for functions and classes
- **Fix Errors**: Automatically fix code errors
- **Refactor Code**: AI-assisted code refactoring
- **Generate Tests**: Create unit tests for your code

### 🎨 AI Panel
Interactive webview panel with:
- Code analysis tools
- Code generation interface
- Code explanation viewer
- Code optimization tools

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   cd vscode-rag-extension
   npm install
   ```
3. Compile the extension:
   ```bash
   npm run compile
   ```
4. Press F5 to run the extension in a new Extension Development Host window

## Configuration

Configure the extension in VS Code settings:

```json
{
  "rag-extension.ragProxyUrl": "http://localhost:3001",
  "rag-extension.enableInlineCompletions": true,
  "rag-extension.enableHoverProvider": true,
  "rag-extension.enableCodeLens": true,
  "rag-extension.maxSuggestions": 3,
  "rag-extension.confidenceThreshold": 0.7,
  "rag-extension.autoSuggestions": true,
  "rag-extension.showConfidence": true
}
```

## Usage

### Keyboard Shortcuts
- `Ctrl+Shift+A` (Cmd+Shift+A on Mac): Open AI Panel
- `Ctrl+Shift+S` (Cmd+Shift+S on Mac): Analyze Selected Code
- `Ctrl+Shift+G` (Cmd+Shift+G on Mac): Generate Code from Comment

### Command Palette
Access all features through the Command Palette (`Ctrl+Shift+P`):
- Search for "RAG" to see all available commands

### Context Menu
Right-click in the editor to access:
- Analyze Selected Code
- Optimize Selected Code
- Refactor Code
- Generate Tests
- Add AI Documentation
- Fix Code Errors

## Prerequisites

This extension requires the following services to be running:

1. **RAG Proxy** (http://localhost:3001)
2. **Ollama** (http://localhost:11434)
3. **LightRAG** (http://localhost:8001)
4. **n8n** (http://localhost:5678)

Use the provided Docker Compose setup to run all services:

```bash
# Copy environment file
cp env.rag-system.example .env

# Start all services
docker-compose -f docker-compose-rag-system.yml up -d
```

## Architecture

The extension consists of several key components:

### Providers
- **AICompletionProvider**: Provides inline code completions
- **AIHoverProvider**: Shows AI explanations on hover
- **AICodeLensProvider**: Displays AI suggestions and improvements

### Services
- **RAGService**: Main service for communicating with the RAG backend

### UI Components
- **AIPanel**: Interactive webview for AI tools
- **QuickActions**: Handles quick action commands

## API Integration

The extension communicates with the RAG system through HTTP APIs:

- `/api/suggestions` - Get code suggestions
- `/api/analyze` - Analyze code
- `/api/generate` - Generate code
- `/api/explain` - Explain code
- `/api/optimize` - Optimize code
- `/api/refactor` - Refactor code
- `/api/generate-tests` - Generate tests
- `/api/fix-error` - Fix code errors

## Development

### Project Structure
```
src/
├── extension.ts          # Main extension entry point
├── providers/            # VS Code providers
│   ├── completion-provider.ts
│   ├── hover-provider.ts
│   ├── code-lens-provider.ts
│   └── index.ts
├── services/             # Backend services
│   └── rag-service.ts
└── ui/                   # UI components
    ├── ai-panel.ts
    ├── quick-actions.ts
    └── index.ts
```

### Building
```bash
npm run compile
```

### Watching
```bash
npm run watch
```

### Testing
```bash
npm test
```

## Troubleshooting

### Extension Not Working
1. Check that all required services are running
2. Verify configuration URLs in settings
3. Check the Developer Console for errors

### Services Not Responding
1. Ensure Docker services are running:
   ```bash
   docker-compose -f docker-compose-rag-system.yml ps
   ```
2. Check service health:
   ```bash
   curl http://localhost:3001/health
   ```

### Performance Issues
1. Reduce `maxSuggestions` in settings
2. Increase `confidenceThreshold` to show fewer suggestions
3. Disable `autoSuggestions` if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Developer Console for errors
3. Create an issue in the repository
