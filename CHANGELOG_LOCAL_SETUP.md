# Changelog: Local LLM Setup

## Summary

This update adds comprehensive support for running Enterprise Deep Research entirely locally using OpenAI-compatible endpoints (Ollama, vLLM, etc.) with no external telemetry.

## Changes

### 1. Modified Files

#### `llm_clients.py`
**Changes:**
- Modified `get_llm_client()` function to support `OPENAI_BASE_URL` environment variable
- Added support for dummy API key (`dummy-key`) when using local endpoints that don't require authentication
- Made temperature configurable via `OPENAI_TEMPERATURE` environment variable (default: 0)
- Updated both synchronous and asynchronous OpenAI client creation functions
- Simplified API key logic based on code review feedback

**Key additions:**
```python
# Support local OpenAI-compatible endpoints
api_key = OPENAI_API_KEY or "dummy-key"
base_url = os.getenv("OPENAI_BASE_URL")
temperature = float(os.getenv("OPENAI_TEMPERATURE", "0"))

# Add base_url to client params if specified
if base_url:
    client_params["base_url"] = base_url
```

#### `.env.sample`
**Changes:**
- Set `LANGCHAIN_TRACING_V2=false` by default (was `true`)
- Added `OTEL_SDK_DISABLED=true` to disable OpenTelemetry
- Added `OPENAI_BASE_URL` configuration with example for Ollama
- Added `OPENAI_TEMPERATURE` configuration option
- Added comprehensive documentation section for local LLM setup

**Key additions:**
```ini
## Telemetry Configuration (Disabled by default for local/privacy) ##
LANGCHAIN_TRACING_V2=false
OTEL_SDK_DISABLED=true

## Local LLM Setup ##
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_TEMPERATURE=0
```

#### `README.md`
**Changes:**
- Added prominent note about local setup with link to `LOCAL_SETUP.md`
- Added section about local LLM configuration in Environment Configuration
- Added "Local (Ollama/vLLM)" row to Supported Models table
- Documented new environment variables: `OPENAI_BASE_URL`, `OPENAI_TEMPERATURE`, `LANGCHAIN_TRACING_V2`, `OTEL_SDK_DISABLED`

### 2. New Files

#### `LOCAL_SETUP.md`
**Purpose:** Comprehensive guide for running Enterprise Deep Research locally

**Contents:**
- Overview of local setup benefits
- Prerequisites and hardware requirements
- Phase 1: Local LLM setup instructions
  - Option A: Ollama (recommended for beginners)
  - Option B: vLLM (advanced users)
- Phase 2: Configuration instructions
  - Environment variable setup
  - Frontend build instructions
- Phase 3: Local search engine setup (optional SearXNG)
- Running the application (full stack, backend only, CLI)
- Security and privacy guidelines
- Model selection recommendations
- Troubleshooting section
- Advanced customization options

#### `.env.local.example`
**Purpose:** Ready-to-use example environment file for local setup

**Contents:**
- Pre-configured settings for Ollama
- Dummy API key
- Local endpoint configuration
- Disabled telemetry settings
- Comprehensive comments explaining each setting

#### `CHANGELOG_LOCAL_SETUP.md`
**Purpose:** This file - documents all changes made for local setup support

## Environment Variables

### New Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_BASE_URL` | (none) | URL for local OpenAI-compatible endpoint (e.g., `http://localhost:11434/v1`) |
| `OPENAI_TEMPERATURE` | `0` | Temperature for OpenAI models (0 = deterministic, 1 = creative) |
| `OTEL_SDK_DISABLED` | `true` | Disables OpenTelemetry SDK |

### Modified Variables

| Variable | Old Default | New Default | Reason |
|----------|-------------|-------------|--------|
| `LANGCHAIN_TRACING_V2` | `true` | `false` | Disable telemetry by default for privacy |

## Compatibility

### Backward Compatibility
All changes are **fully backward compatible**:
- Existing users with cloud API keys continue to work unchanged
- Default behavior only changes for telemetry (now disabled by default)
- New environment variables are optional

### Tested Configurations
- ✅ Local Ollama with llama3.1:8b
- ✅ Dummy API key with local endpoint
- ✅ Custom temperature settings
- ✅ Telemetry disabled
- ✅ Synchronous client creation
- ✅ Asynchronous client creation

## Usage Examples

### Example 1: Basic Local Setup (Ollama)
```bash
# .env file
LLM_PROVIDER=openai
LLM_MODEL=llama3.1:8b
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:11434/v1
LANGCHAIN_TRACING_V2=false
```

### Example 2: vLLM with Custom Port
```bash
# .env file
LLM_PROVIDER=openai
LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:8000/v1
LANGCHAIN_TRACING_V2=false
```

### Example 3: Custom Temperature
```bash
# .env file
LLM_PROVIDER=openai
LLM_MODEL=llama3.1:8b
OPENAI_API_KEY=dummy-key
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_TEMPERATURE=0.7  # More creative responses
```

## Security Considerations

### Privacy Benefits
1. **No External API Calls:** All LLM inference happens locally
2. **No Telemetry:** LangSmith and OpenTelemetry disabled by default
3. **Data Control:** All research data stays on your machine
4. **Optional Local Search:** Can use SearXNG for fully private web search

### Verification
Users can verify no external calls by monitoring network traffic:
```bash
sudo tcpdump -i any -n 'not (host localhost or host 127.0.0.1)' | grep -v '443'
```

## Testing

### Test Coverage
- ✅ LLM client initialization with local endpoint
- ✅ API key handling (dummy key support)
- ✅ Base URL configuration
- ✅ Temperature configuration
- ✅ Telemetry disabled by default
- ✅ Configuration class loading
- ✅ Async client support
- ✅ Security scanning (CodeQL - no vulnerabilities)

### Test Commands
```bash
# Run local LLM tests
python /tmp/test_local_llm.py

# Run integration tests
python /tmp/test_integration.py
```

## Migration Guide

### For Existing Users
No migration needed - existing configurations continue to work unchanged.

### For New Users (Local Setup)
1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Pull a model: `ollama pull llama3.1:8b`
3. Copy local example: `cp .env.local.example .env`
4. Adjust settings in `.env` as needed
5. Run: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`

## Known Limitations

1. **Search still requires API key:** Tavily API is still required for web search (unless implementing custom SearXNG integration)
2. **Custom reasoning models:** o3-mini and o4-mini reasoning modes may not work with all local models
3. **Performance:** Local models may be slower than cloud APIs depending on hardware

## Future Enhancements

Potential future improvements:
- [ ] Built-in SearXNG integration as search provider option
- [ ] Support for more local LLM providers
- [ ] Performance optimization guides for different hardware
- [ ] Docker compose setup for full local stack
- [ ] Benchmark comparisons: local vs cloud models

## References

- [Local Setup Guide](LOCAL_SETUP.md)
- [Main README](README.md)
- [Ollama Documentation](https://ollama.com/docs)
- [vLLM Documentation](https://docs.vllm.ai/)
- [SearXNG Documentation](https://docs.searxng.org/)

## Version

- **Version:** 1.0.0
- **Date:** December 2024
- **Author:** Enterprise Deep Research Contributors
