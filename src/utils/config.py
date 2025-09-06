"""
Configuration utility functions.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment variables."""
    
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "database_path": os.getenv("DATABASE_PATH", "data/pdf_extractor.db"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "52428800")),  # 50MB
        "supported_formats": [".pdf"],
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-5-nano"),
        "default_temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
        "default_max_tokens": int(os.getenv("DEFAULT_MAX_TOKENS", "1000")),
        "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "1")),
    }
    
    # Try to load from config file if specified
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    return config


def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate configuration values."""
    
    errors = []
    
    # Check required fields
    if not config.get("openai_api_key"):
        errors.append("OpenAI API key is required")
    
    # Validate numeric values
    if config.get("max_file_size", 0) <= 0:
        errors.append("Max file size must be positive")
    
    if not (0 <= config.get("default_temperature", 0) <= 2):
        errors.append("Default temperature must be between 0 and 2")
    
    if not (100 <= config.get("default_max_tokens", 0) <= 4000):
        errors.append("Default max tokens must be between 100 and 4000")
    
    if config.get("retry_attempts", 0) < 0:
        errors.append("Retry attempts must be non-negative")
    
    if config.get("retry_delay", 0) < 0:
        errors.append("Retry delay must be non-negative")
    
    return len(errors) == 0, errors


def create_default_config(config_path: str = "config.json") -> bool:
    """Create a default configuration file."""
    
    default_config = {
        "openai_api_key": "your-api-key-here",
        "database_path": "data/pdf_extractor.db",
        "log_level": "INFO",
        "max_file_size": 52428800,
        "supported_formats": [".pdf"],
        "default_model": "gpt-5-nano",
        "default_temperature": 0.1,
        "default_max_tokens": 1000,
        "retry_attempts": 3,
        "retry_delay": 1,
        "form_templates": {
            "customer_registration": {
                "name": "Customer Registration",
                "description": "General customer registration forms",
                "extraction_fields": ["customer_name", "email", "phone", "address", "date_of_birth"]
            },
            "insurance_claim": {
                "name": "Insurance Claim",
                "description": "Insurance claim forms",
                "extraction_fields": ["claim_number", "policy_number", "claim_type", "incident_date", "damage_description"]
            }
        }
    }
    
    try:
        # Ensure directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error creating config file: {e}")
        return False
