import os
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger

# LangChain 1.0 imports
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.callbacks import AsyncCallbackHandler

# 本地配置
from config import settings

# 加载环境变量
load_dotenv(override=True)

# 配置日志
logger.add(settings.log_file, rotation="500 MB", level=settings.log_level)

app = FastAPI(
    title="多模态 RAG 工作台 API",
    description="基于 LangChain 1.0 的智能对话 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class MessageRequest(BaseModel):
    content: str = Field(..., description="用户消息内容")
    history: List[Dict[str, Any]] = Field(default=[], description="对话历史")
    model: str = Field(default="gpt-4o", description="使用的模型")
    knowledge_base: str = Field(default="default", description="知识库名称")

class MessageResponse(BaseModel):
    content: str
    role: str
    timestamp: str
    references: List[Dict[str, Any]] = Field(default=[])

# 流式回调处理器
class StreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        self.tokens = []
        self.current_chunk = ""
        
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """处理新的 token"""
        self.tokens.append(token)
        self.current_chunk += token

# 初始化聊天模型
def get_chat_model(model_name: str = None):
    """初始化聊天模型"""
    if model_name is None:
        model_name = settings.default_model
        
    try:
        # 使用 LangChain 1.0 的新方式初始化模型
        model = init_chat_model(
            f"openai:{model_name}",
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            streaming=True
        )
        return model
    except Exception as e:
        logger.error(f"初始化模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")

def convert_history_to_messages(history: List[Dict[str, Any]]) -> List[BaseMessage]:
    """将历史记录转换为 LangChain 消息格式"""
    messages = []
    
    # 添加系统消息
    system_prompt = """你是一个专业的多模态 RAG 助手，具备以下能力：
1. 文档理解与分析
2. 图像内容识别
3. 音频转写与分析
4. 知识检索与问答

请以专业、友好的方式回答用户问题，并在需要时提供详细的解释。"""
    
    messages.append(SystemMessage(content=system_prompt))
    
    # 转换历史消息
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    return messages

async def generate_streaming_response(
    messages: List[BaseMessage], 
    model_name: str
) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        model = get_chat_model(model_name)
        
        # 创建流式响应
        full_response = ""
        chunk_buffer = ""
        
        async for chunk in model.astream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_response += content
                chunk_buffer += content
                
                # 按句子或短语分块发送
                if any(delimiter in chunk_buffer for delimiter in ['.', '。', '!', '！', '?', '？', '\n']):
                    # 构造 SSE 格式的数据
                    data = {
                        "type": "content_delta",
                        "content": chunk_buffer,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    chunk_buffer = ""
                else:
                    # 发送单个字符
                    data = {
                        "type": "content_delta",
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        # 发送剩余内容
        if chunk_buffer:
            data = {
                "type": "content_delta",
                "content": chunk_buffer,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        # 发送完成信号
        final_data = {
            "type": "message_complete",
            "full_content": full_response,
            "timestamp": datetime.now().isoformat(),
            "references": []  # 暂时为空，后续可添加 RAG 引用
        }
        yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        logger.error(f"流式响应生成失败: {e}")
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "message": "多模态 RAG 工作台 API",
        "version": "1.0.0",
        "status": "running",
        "langchain_version": "1.0.0"
    }

@app.post("/api/chat/stream")
async def chat_stream(request: MessageRequest):
    """流式聊天接口"""
    try:
        logger.info(f"收到聊天请求: {request.content[:100]}...")
        
        # 转换消息历史
        messages = convert_history_to_messages(request.history)
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=request.content))
        
        # 返回流式响应
        return StreamingResponse(
            generate_streaming_response(messages, request.model),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_sync(request: MessageRequest):
    """同步聊天接口（非流式）"""
    try:
        logger.info(f"收到同步聊天请求: {request.content[:100]}...")
        
        # 转换消息历史
        messages = convert_history_to_messages(request.history)
        messages.append(HumanMessage(content=request.content))
        
        # 获取模型响应
        model = get_chat_model(request.model)
        response = await model.ainvoke(messages)
        
        return MessageResponse(
            content=response.content,
            role="assistant",
            timestamp=datetime.now().isoformat(),
            references=[]
        )
        
    except Exception as e:
        logger.error(f"同步聊天请求处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """获取可用模型列表"""
    return {
        "models": [
            {
                "id": "gpt-4o",
                "name": "GPT-4O",
                "description": "最新的 GPT-4 优化版本"
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4O Mini",
                "description": "轻量级 GPT-4 版本"
            },
            {
                "id": "gpt-5",
                "name": "GPT-5",
                "description": "下一代 GPT 模型（如果可用）"
            }
        ]
    }

@app.get("/api/knowledge-bases")
async def get_knowledge_bases():
    """获取知识库列表"""
    return {
        "knowledge_bases": [
            {
                "id": "default",
                "name": "默认知识库",
                "description": "通用知识库"
            },
            {
                "id": "technical",
                "name": "技术文档",
                "description": "技术相关文档库"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    ) 