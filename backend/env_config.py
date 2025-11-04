#!/usr/bin/env python3
"""
环境配置设置
请在使用前设置你的 OpenAI API Key
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

def setup_environment():
    """设置环境变量"""
    
    # OpenAI 配置
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  请设置你的 OPENAI_API_KEY")
        print("💡 在 .env 文件中设置: OPENAI_API_KEY=your_actual_api_key")
        print("💡 或在系统环境变量中设置")
        # 不要硬编码设置无效的API key
        # os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
    
    os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
    
    # 服务器配置
    os.environ["HOST"] = "localhost"
    os.environ["PORT"] = "8000"
    os.environ["DEBUG"] = "True"
    
    # 日志配置
    os.environ["LOG_LEVEL"] = "INFO"
    
    # 模型配置
    os.environ["DEFAULT_MODEL"] = "gpt-4o"
    os.environ["MAX_TOKENS"] = "2048"
    os.environ["TEMPERATURE"] = "0.7"
    
    # OCR配置 - Tesseract
    tessdata_path = r"C:\ProgramData\anaconda3\envs\rag\share\tessdata"
    os.environ["TESSDATA_PREFIX"] = tessdata_path
    print(f"✅ TESSDATA_PREFIX 已设置: {tessdata_path}")

if __name__ == "__main__":
    setup_environment()
    print("✅ 环境变量设置完成")
    print("💡 请修改 env_config.py 中的 OPENAI_API_KEY") 