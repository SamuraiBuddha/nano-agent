"""
Extended Provider Configuration with LM Studio Support.

This module extends the original provider_config.py to add LM Studio support.
LM Studio runs an OpenAI-compatible server at http://192.168.50.30:1234/v1/chat/completions
"""

from typing import Optional
import os
import logging
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, ModelSettings
import requests

logger = logging.getLogger(__name__)


class ProviderConfigExtended:
    """Extended configuration including LM Studio."""
    
    @staticmethod
    def create_agent(
        name: str,
        instructions: str,
        tools: list,
        model: str,
        provider: str,
        model_settings: Optional[ModelSettings] = None
    ) -> Agent:
        """Create an agent with LM Studio support added.
        
        Providers:
        - 'openai': Standard OpenAI
        - 'anthropic': Claude via OpenAI-compatible endpoint
        - 'ollama': Local Ollama server
        - 'lmstudio': LM Studio at 192.168.50.30:1234
        """
        
        if provider == "lmstudio":
            # LM Studio configuration
            logger.debug(f"Creating LM Studio agent with model: {model}")
            lmstudio_client = AsyncOpenAI(
                base_url="http://192.168.50.30:1234/v1",
                api_key="not-needed"  # LM Studio doesn't require API key
            )
            return Agent(
                name=name,
                instructions=instructions,
                tools=tools,
                model=OpenAIChatCompletionsModel(
                    model=model,
                    openai_client=lmstudio_client
                ),
                model_settings=model_settings
            )
        
        # Fall back to original implementation for other providers
        # (Would import from original provider_config.py in production)
        else:
            raise ValueError(f"Use this for LM Studio only. Got: {provider}")
    
    @staticmethod
    def validate_lmstudio_setup(model: str) -> tuple[bool, Optional[str]]:
        """Validate that LM Studio is running and model is loaded.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if LM Studio server is running
            response = requests.get("http://192.168.50.30:1234/v1/models", timeout=2)
            if response.status_code == 200:
                models = response.json().get("data", [])
                model_ids = [m.get("id") for m in models]
                
                if not models:
                    return False, "No models loaded in LM Studio. Load a model first."
                
                # If specific model requested, check if it's loaded
                if model != "default" and model not in model_ids:
                    available = ", ".join(model_ids)
                    return False, f"Model '{model}' not loaded. Available: {available}"
                
                return True, None
            else:
                return False, f"LM Studio server error: {response.status_code}"
                
        except requests.ConnectionError:
            return False, "LM Studio not reachable at http://192.168.50.30:1234. Is it running?"
        except requests.Timeout:
            return False, "LM Studio timeout. Check if server is responding."
        except Exception as e:
            return False, f"Error checking LM Studio: {str(e)}"


# Quick test function
def test_lmstudio_connection():
    """Test if LM Studio is accessible."""
    is_valid, error = ProviderConfigExtended.validate_lmstudio_setup("default")
    if is_valid:
        print("✅ LM Studio is running and ready!")
        # Get loaded models
        response = requests.get("http://192.168.50.30:1234/v1/models")
        models = response.json().get("data", [])
        print(f"Loaded models: {[m.get('id') for m in models]}")
    else:
        print(f"❌ LM Studio error: {error}")


if __name__ == "__main__":
    test_lmstudio_connection()