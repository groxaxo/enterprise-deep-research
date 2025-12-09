# Local Setup Guide for Enterprise Deep Research

This guide provides detailed instructions for running Enterprise Deep Research entirely locally on an Ubuntu server with no external telemetry and using local OpenAI-compatible endpoints.

## 🎯 Overview

This setup enables you to:
- Run all LLM inference locally using Ollama, vLLM, or similar OpenAI-compatible servers
- Disable all external telemetry and tracking
- Optionally use local search engines (SearXNG) for fully private operation
- Maintain complete data privacy and control

## 📋 Prerequisites

- Ubuntu 20.04+ (or similar Linux distribution)
- Python 3.11+
- Docker (optional, for SearXNG)
- At least 16GB RAM (32GB+ recommended for larger models)
- GPU with 8GB+ VRAM (optional but recommended for better performance)

## 🚀 Phase 1: Local LLM Setup

### Option A: Ollama (Recommended for Beginners)

Ollama is the easiest way to run local LLMs with an OpenAI-compatible API.

#### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Pull a Model

Choose a model based on your hardware:

**For systems with 8GB+ VRAM:**
```bash
ollama pull llama3.1:8b
```

**For systems with 24GB+ VRAM:**
```bash
ollama pull llama3.1:70b
```

**Alternative models:**
```bash
# Qwen2.5 (good for coding and reasoning)
ollama pull qwen2.5:14b

# Mistral (fast and efficient)
ollama pull mistral:7b

# DeepSeek (excellent for reasoning)
ollama pull deepseek-r1:8b
```

#### 3. Verify Ollama is Running

Ollama automatically starts as a service. Verify it's accessible:

```bash
curl http://localhost:11434/v1/models
```

You should see a list of available models.

### Option B: vLLM (Advanced Users)

vLLM provides higher throughput and is better for production workloads.

#### 1. Install vLLM

```bash
pip install vllm
```

#### 2. Start vLLM Server

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 11434 \
    --host 0.0.0.0
```

Or with GPU acceleration:

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 11434 \
    --host 0.0.0.0 \
    --tensor-parallel-size 1
```

## 🔧 Phase 2: Configure Enterprise Deep Research

### 1. Clone and Setup the Repository

```bash
git clone https://github.com/SalesforceAIResearch/enterprise-deep-research.git
cd enterprise-deep-research

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

For a quick start with local setup, copy the local example:

```bash
cp .env.local.example .env
```

Or create from the general sample:

```bash
cp .env.sample .env
```

Edit the `.env` file with your local configuration:

```ini
# Local LLM Configuration (Ollama Example)
LLM_PROVIDER=openai
LLM_MODEL=llama3.1:8b
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:11434/v1

# Search Configuration
# Keep Tavily if you want web search (requires API key)
SEARCH_API=tavily
TAVILY_API_KEY=your-tavily-key-here

# OR use local SearXNG (see Phase 3 below)
# SEARCH_API=tavily  # Keep this for now, we'll add SearXNG support

# Research Configuration
MAX_WEB_RESEARCH_LOOPS=3
FETCH_FULL_PAGE=True

# Telemetry - DISABLED for privacy
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=""
LANGCHAIN_PROJECT=""
OTEL_SDK_DISABLED=true

# Activity Generation - Use same local LLM
ENABLE_ACTIVITY_GENERATION=true
ACTIVITY_VERBOSITY=medium
ACTIVITY_LLM_PROVIDER=openai
ACTIVITY_LLM_MODEL=llama3.1:8b
```

### 3. Build Frontend (Optional)

If you want to use the web interface:

```bash
cd ai-research-assistant
npm install
npm run build
cd ..
```

## 🔍 Phase 3: Local Search Engine (Optional)

For completely local operation without external API calls, you can set up SearXNG.

### 1. Install SearXNG via Docker

```bash
docker run -d \
    -p 8080:8080 \
    --name searxng \
    --restart unless-stopped \
    searxng/searxng:latest
```

### 2. Verify SearXNG is Running

Open http://localhost:8080 in your browser. You should see the SearXNG search interface.

### 3. Configure Enterprise Deep Research for SearXNG

**Note:** The current version uses Tavily for search. To use SearXNG, you would need to implement a custom search tool. This is documented in the "Advanced Customization" section below.

## 🏃 Running the Application

### Full Stack Mode (Backend + Frontend)

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Access the application at http://localhost:8000

### Backend Only

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Access the API documentation at http://localhost:8000/docs

### Command Line Usage

```bash
python benchmarks/run_research.py "Your research question" \
    --provider openai \
    --model llama3.1:8b \
    --max-loops 3
```

## 🔐 Security and Privacy

### Telemetry Status

All telemetry is disabled by default with these settings:
- `LANGCHAIN_TRACING_V2=false` - Disables LangSmith tracing
- `OTEL_SDK_DISABLED=true` - Disables OpenTelemetry SDK
- No analytics libraries in the frontend

### Data Privacy

- All LLM inference runs locally on your machine
- No data is sent to external services (except web search if using Tavily)
- For complete privacy, use SearXNG for local search

### Verifying No External Calls

You can monitor network traffic to verify no external API calls:

```bash
# Install tcpdump
sudo apt-get install tcpdump

# Monitor network traffic (run in separate terminal)
sudo tcpdump -i any -n 'not (host localhost or host 127.0.0.1)' | grep -v '443'
```

## 🎛️ Model Selection

### Recommended Models by Use Case

| Use Case | Model | VRAM Required | Speed |
|----------|-------|---------------|-------|
| Quick testing | llama3.1:8b | 8GB | Fast |
| Balanced performance | qwen2.5:14b | 14GB | Medium |
| Best quality | llama3.1:70b | 40GB+ | Slow |
| Reasoning tasks | deepseek-r1:8b | 8GB | Medium |
| Coding | qwen2.5-coder:7b | 8GB | Fast |

### Performance Tuning

For better performance with Ollama:

```bash
# Use GPU acceleration (automatically detected)
ollama serve

# Adjust context length (if needed)
# Edit ~/.ollama/models/<model>/config.json
# Set "num_ctx": 8192  # or higher
```

## 🛠️ Troubleshooting

### Issue: Model Not Found

```bash
# List available models
ollama list

# Pull the model if missing
ollama pull llama3.1:8b
```

### Issue: Connection Refused

```bash
# Check if Ollama is running
curl http://localhost:11434/v1/models

# Restart Ollama
systemctl restart ollama  # or
sudo systemctl restart ollama
```

### Issue: Out of Memory

- Use a smaller model (e.g., mistral:7b instead of llama3.1:70b)
- Reduce `MAX_WEB_RESEARCH_LOOPS` in .env
- Close other applications to free up RAM/VRAM

### Issue: Slow Performance

- Ensure GPU is being used (check with `nvidia-smi`)
- Use quantized models (e.g., llama3.1:8b-q4 instead of llama3.1:8b)
- Reduce context length in model config

## 📚 Advanced Customization

### Using SearXNG Instead of Tavily

To implement SearXNG support, you need to modify `src/tools/search_tools.py` and `src/utils.py`:

1. Install SearXNG Python client:
```bash
pip install searxng-client
```

2. Create a custom search function in `src/utils.py`:
```python
import requests

def searxng_search(query, top_k=5, searxng_url="http://localhost:8080"):
    """Search using local SearXNG instance."""
    params = {
        'q': query,
        'format': 'json',
        'pageno': 1
    }
    
    response = requests.get(f"{searxng_url}/search", params=params)
    results = response.json()
    
    # Format results to match Tavily structure
    formatted_results = []
    for result in results.get('results', [])[:top_k]:
        formatted_results.append({
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'raw_content': result.get('content', '')
        })
    
    return {'results': formatted_results}
```

3. Update search tools to use SearXNG when configured.

### Custom Model Configuration

To use different model endpoints:

```bash
# Custom endpoint
export OPENAI_BASE_URL=http://custom-server:8000/v1

# Different port for Ollama
export OPENAI_BASE_URL=http://localhost:12345/v1
```

### Multi-Model Setup

You can use different models for different tasks:

```ini
# Main research model
LLM_PROVIDER=openai
LLM_MODEL=llama3.1:70b
OPENAI_BASE_URL=http://localhost:11434/v1

# Faster model for activity generation
ACTIVITY_LLM_PROVIDER=openai
ACTIVITY_LLM_MODEL=mistral:7b
```

## 📊 Monitoring and Logs

### Application Logs

Logs are written to `backend_logs.txt` in the application directory.

```bash
# Watch logs in real-time
tail -f backend_logs.txt
```

### Ollama Logs

```bash
# View Ollama logs
journalctl -u ollama -f
```

### Performance Monitoring

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Monitor CPU and RAM
htop
```

## 🤝 Contributing

If you make improvements to the local setup, please consider contributing back to the project!

## 📄 License

This project is licensed under Apache 2.0. See LICENSE.txt for details.

## 🆘 Support

For issues specific to local setup:
1. Check the troubleshooting section above
2. Review Ollama documentation: https://ollama.com/docs
3. Open an issue on GitHub with the `local-setup` label

For general project issues, refer to the main README.md.
