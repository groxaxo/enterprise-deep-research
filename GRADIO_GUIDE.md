# Gradio Interface Guide

This guide provides detailed information about using the Gradio 6 interface for Enterprise Deep Research.

## 🚀 Quick Start

Launch the Gradio interface with a single command:

```bash
python gradio_app.py
```

The interface will be available at [http://localhost:7860](http://localhost:7860)

## 📋 Prerequisites

### Required
- Python 3.11+
- Gradio 6.0+ (automatically installed from requirements.txt)
- At least one LLM provider API key
- Tavily API key for web search

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install just Gradio
pip install "gradio>=6.0.0"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: LLM Provider (choose one or more)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_CLOUD_PROJECT=your-google-project-id
GROQ_API_KEY=your-groq-key-here
SAMBANOVA_API_KEY=your-sambanova-key-here

# Required: Search API
TAVILY_API_KEY=your-tavily-key-here

# Optional: Default Configuration
LLM_PROVIDER=openai          # Default: openai
LLM_MODEL=o3-mini            # Default: o3-mini
MAX_WEB_RESEARCH_LOOPS=10    # Default: 10

# Optional: Privacy Settings
LANGCHAIN_TRACING_V2=false   # Disable telemetry
OTEL_SDK_DISABLED=true       # Disable OpenTelemetry
```

### Local LLM Setup (Ollama/vLLM)

For fully local deployment:

```bash
# Point to local endpoint
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=dummy-key
LLM_MODEL=llama3.1:8b

# Disable telemetry
LANGCHAIN_TRACING_V2=false
OTEL_SDK_DISABLED=true
```

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed local deployment instructions.

## 🎨 Interface Features

### Main Research Tab

The primary interface for conducting deep research:

#### Input Section
- **Research Query**: Enter your research question or topic
- **File Upload**: Upload documents (PDF, TXT, DOCX, CSV, JSON) to include in research context
- **Provider Selection**: Choose from OpenAI, Anthropic, Google, Groq, or SambaNova
- **Model Selection**: Select specific model (options update based on provider)
- **Max Research Loops**: Control research depth (1-20 loops)
  - Lower values (1-3): Quick research
  - Medium values (5-10): Balanced research
  - Higher values (15-20): Deep, comprehensive research
- **Extra Effort Mode**: Enable for more extensive research
- **Quick Mode**: Force minimum effort (1 loop only)
- **Enable Steering**: Allow real-time guidance during research

#### Output Section
- **Status**: Real-time status updates
- **Research Report**: Formatted markdown report with findings
- **Sources**: List of all sources used in the research

### About Tab

Comprehensive information about Enterprise Deep Research:
- System overview and architecture
- Key features and capabilities
- Documentation links
- Citation information
- Acknowledgments

### Settings Tab

View current configuration:
- LLM provider and model settings
- API key status indicators
- Privacy settings
- Configuration instructions

## 📊 Usage Examples

### Basic Research

1. Enter your query: "Latest developments in quantum computing"
2. Select provider (e.g., OpenAI) and model (e.g., o3-mini)
3. Set max loops to 5-10
4. Click "Start Research"
5. View results in the output panel

### Research with Documents

1. Enter your query: "Analyze this financial report"
2. Click "Upload documents" and select your PDF/DOCX files
3. Configure provider and model
4. Click "Start Research"
5. The system will analyze uploaded documents as part of the research

### Quick Research

1. Enter a simple query: "Who is the CEO of Tesla?"
2. Enable "Quick Mode" checkbox
3. This forces 1 loop for fast results
4. Click "Start Research"

### Deep Research

1. Enter a complex query: "Comprehensive analysis of AI safety research landscape"
2. Enable "Extra Effort Mode"
3. Set max loops to 15-20
4. Optionally enable "Steering" for guidance
5. Click "Start Research"

## 🔧 Advanced Features

### Real-time Steering

When enabled, steering allows you to guide the research process:

1. Enable "Enable Steering" checkbox
2. Start research
3. Monitor progress
4. Provide guidance through steering commands
5. System adapts research direction based on feedback

Note: Full steering functionality requires the backend API to be running.

### File Analysis

The interface supports multiple file formats:
- **Text**: .txt, .md
- **Documents**: .pdf, .docx
- **Data**: .csv, .json
- **Images**: .png, .jpg (with OCR if configured)

Files are processed and included in the research context automatically.

### Provider and Model Selection

Different providers offer different capabilities:

| Provider | Best For | Speed | Quality |
|----------|----------|-------|---------|
| OpenAI (o3-mini) | Balanced performance | Fast | High |
| Anthropic (Claude) | Complex reasoning | Medium | Very High |
| Google (Gemini) | Multimodal tasks | Fast | High |
| Groq (DeepSeek) | Cost-effective | Very Fast | Good |
| Local (Ollama) | Privacy, offline | Variable | Variable |

## 🚨 Troubleshooting

### Interface won't start

```bash
# Check if port 7860 is already in use
lsof -i :7860

# Kill any existing process
kill <PID>

# Or use a different port
# Edit gradio_app.py, line ~605: server_port=7861
```

### "No module named 'gradio'"

```bash
# Install Gradio
pip install "gradio>=6.0.0"

# Or install all requirements
pip install -r requirements.txt
```

### "API key not found" warnings

1. Check your `.env` file exists
2. Verify API keys are set correctly
3. Restart the application after updating `.env`

### Research fails with "Rate limit exceeded"

1. Check your API provider account limits
2. Reduce "Max Research Loops" value
3. Wait a few minutes before retrying
4. Consider using a different provider

### File upload not working

1. Ensure files are in supported formats
2. Check file size (large files may timeout)
3. Try uploading one file at a time
4. Check console for specific error messages

## 🔒 Security and Privacy

### API Keys

- Never commit `.env` files to version control
- Use environment variables for production deployment
- Rotate API keys regularly

### Data Privacy

- All research data is processed through your chosen LLM provider
- Enable local mode (Ollama/vLLM) for complete privacy
- Disable telemetry with `LANGCHAIN_TRACING_V2=false`

### Network Security

- By default, interface binds to `0.0.0.0` (all interfaces)
- For localhost only, edit `gradio_app.py`: `server_name="127.0.0.1"`
- Use a reverse proxy (nginx) for production deployment

## 📱 Mobile Access

The Gradio interface is responsive and works on mobile devices:

1. Ensure your device is on the same network
2. Find your computer's IP address: `hostname -I`
3. Access: `http://YOUR_IP:7860`
4. Or use Gradio's share feature (see below)

### Gradio Share

To create a public shareable link:

Edit `gradio_app.py`, line ~606:
```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,  # Enable sharing
    # ...
)
```

**Warning**: Share links are public. Anyone with the link can access your interface.

## 🎯 Best Practices

### Research Queries

- Be specific and clear
- Include context when needed
- Use proper formatting for complex queries
- Break down very complex topics into multiple queries

### Configuration

- Start with default settings
- Adjust max loops based on query complexity
- Use Extra Effort for comprehensive research
- Enable Quick Mode for simple fact-checking

### Performance

- Lower max loops for faster results
- Use Groq for quick iterations
- Use Anthropic/OpenAI for quality
- Monitor API usage and costs

## 🆚 Gradio vs React Frontend

| Feature | Gradio Interface | React Frontend |
|---------|-----------------|----------------|
| Setup | Instant | Requires npm build |
| Updates | Auto-reload | Manual rebuild |
| Customization | Python-based | Full control |
| Mobile | Responsive | Responsive |
| API Access | Built-in | Requires backend |
| Sharing | Easy (built-in) | Complex |
| Best For | Quick start, demos | Production |

## 📚 Additional Resources

- [Gradio Documentation](https://gradio.app/docs)
- [Enterprise Deep Research Paper](https://arxiv.org/abs/2510.17797)
- [EDR-200 Dataset](https://huggingface.co/datasets/Salesforce/EDR-200)
- [Main Documentation](https://deepwiki.com/SalesforceAIResearch/enterprise-deep-research)

## 🤝 Contributing

Improvements to the Gradio interface are welcome!

Areas for enhancement:
- Additional visualization options
- Real-time streaming progress bars
- Database query interface
- Enhanced file processing
- More customization options

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📜 License

Licensed under Apache 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## 🙏 Acknowledgments

The Gradio interface builds upon:
- [Gradio 6](https://gradio.app) - Modern ML web interfaces
- [Enterprise Deep Research](https://github.com/SalesforceAIResearch/enterprise-deep-research) - Core research system
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API framework
