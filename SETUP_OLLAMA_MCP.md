# Nano-Agent MCP Server Setup with Ollama

## Current Status
- **UV Package Manager**: Installed (v0.8.22) ✅
- **Ollama Service**: Running on localhost:11434 ✅
- **Available Models**: gpt-oss:20b (configured in constants.py) ✅
- **Nano-Agent**: Not yet installed ❌

## Installation Steps

### 1. Install Nano-Agent Dependencies
```bash
cd C:\Users\JordanEhrig\Documents\GitHub\nano-agent\apps\nano_agent_mcp_server
uv sync
```

### 2. Verify Installation
```bash
# Test the CLI directly
uv run nano-agent --prompt "List files in current directory" --model gpt-oss:20b --provider ollama
```

### 3. Configure Claude Code to Use Nano-Agent MCP

Add to Claude Code's MCP settings (settings.json):

```json
{
  "mcpServers": {
    "nano-agent": {
      "command": "uv",
      "args": [
        "run",
        "nano-agent"
      ],
      "cwd": "C:\\Users\\JordanEhrig\\Documents\\GitHub\\nano-agent\\apps\\nano_agent_mcp_server",
      "env": {
        "PYTHONPATH": "C:\\Users\\JordanEhrig\\Documents\\GitHub\\nano-agent\\apps\\nano_agent_mcp_server\\src"
      }
    }
  }
}
```

## Usage in Claude Code

Once configured, you can use the `prompt_nano_agent` tool:

```python
# Example tool call
prompt_nano_agent(
    agentic_prompt="Create a Python function that calculates fibonacci numbers",
    model="gpt-oss:20b",
    provider="ollama"
)
```

## Available Ollama Models

From `http://localhost:11434/api/tags`:
- gpt-oss:20b (20.9B parameters, MXFP4 quantization) - Configured in nano-agent
- bakllava:latest (7B, multimodal)
- llava-phi3:latest (4B, multimodal)
- llava:13b (13B, multimodal)
- llava:34b (34B, multimodal)
- llava-llama3:latest (8B, multimodal)
- mangiucugna/bakllava-1:latest (7B)

## Configuration Files

### Provider Configuration (`provider_config.py:113-129`)
```python
elif provider == "ollama":
    ollama_client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Dummy key required by client
    )
    return Agent(
        name=name,
        instructions=instructions,
        tools=tools,
        model=OpenAIChatCompletionsModel(
            model=model,
            openai_client=ollama_client
        ),
        model_settings=model_settings
    )
```

### Constants (`constants.py`)
- **Line 21**: Ollama models: `["gpt-oss:20b", "gpt-oss:120b"]`
- **Line 42**: No API key required for Ollama

## Architecture

```
Claude Code (You)
    ↓ MCP Protocol
nano-agent MCP Server
    ↓ OpenAI SDK with Ollama endpoint
Ollama Service (localhost:11434)
    ↓
Local GPT-OSS Model
```

## Troubleshooting

1. **Ollama not running**: Start with `ollama serve`
2. **Model not available**: Pull with `ollama pull gpt-oss:20b`
3. **UV not installed**: Install with `pip install uv`
4. **Dependencies fail**: Ensure Python >=3.11

## Key Insights

- Nano-agent uses OpenAI SDK's AsyncOpenAI client configured for Ollama's OpenAI-compatible endpoint
- No API keys required for Ollama (uses dummy key "ollama")
- The architecture allows swapping between OpenAI, Anthropic, and Ollama seamlessly
- All providers use the same Agent interface from openai-agents library