import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI 配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    
    # 服务器配置
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # CORS 配置
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 模型配置
    default_model: str = "gpt-4o"
    max_tokens: int = 2048
    temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings() 