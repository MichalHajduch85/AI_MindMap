"""Application configuration with automatic environment loading."""

import os
from pathlib import Path
from typing import Type


class BaseConfig:
    """Base configuration class with environment auto-loading."""
    
    def __init__(self):
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
    
    # Flask Core Settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URI', 'sqlite:///mindmap.db')
    
    # LLM API Settings
    LLM_API_ENDPOINT: str = os.getenv('LLM_API_ENDPOINT', 'http://localhost:11434/api/generate')
    LLM_MODEL_NAME: str = os.getenv('LLM_MODEL_NAME', 'llama3:latest')
    LLM_TIMEOUT_SECONDS: int = int(os.getenv('LLM_TIMEOUT_SECONDS', '180'))
    
    # Hugging Face Settings
    USE_HUGGINGFACE: bool = os.getenv('USE_HUGGINGFACE', 'false').lower() == 'true'
    HUGGINGFACE_TOKEN: str = os.getenv('HUGGINGFACE_TOKEN', '')
    HUGGINGFACE_PROVIDER: str = os.getenv('HUGGINGFACE_PROVIDER', 'together')
    HUGGINGFACE_MODEL: str = os.getenv('HUGGINGFACE_MODEL', 'deepseek-ai/DeepSeek-R1')
    HF_TIMEOUT_SECONDS: int = int(os.getenv('HF_TIMEOUT_SECONDS', '30'))
    
    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    TESTING: bool = os.getenv('TESTING', 'false').lower() == 'true'
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '86400'))


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI', 'sqlite:///dev_mindmap.db')


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI', 'postgresql://user:password@localhost/mindmap_prod')


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite:///:memory:')


def get_config() -> Type[BaseConfig]:
    """Get configuration class based on environment."""
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)