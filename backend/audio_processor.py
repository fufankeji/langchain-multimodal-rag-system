import os
import tempfile
import base64
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from openai import OpenAI
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from config import settings

class AudioProcessor:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
    
    def process_audio_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        处理音频文件：转换格式、语音转文字
        
        Args:
            file_path: 音频文件路径
            filename: 原始文件名
            
        Returns:
            包含转写结果的字典
        """
        try:
            logger.info(f"开始处理音频文件: {filename}")
            
            # 检测文件类型
            file_ext = Path(filename).suffix.lower()
            logger.info(f"文件格式: {file_ext}")
            
            # 转换为支持的音频格式
            audio_path = self._convert_to_audio(file_path, file_ext)
            
            # 语音转文字
            transcription = self._transcribe_audio(audio_path)
            
            # 清理临时文件
            if audio_path != file_path:
                os.unlink(audio_path)
            
            result = {
                "filename": filename,
                "transcription": transcription,
                "duration": self._get_audio_duration(file_path, file_ext),
                "format": file_ext
            }
            
            logger.info(f"✅ 音频处理完成: {len(transcription)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"❌ 音频处理失败: {e}")
            raise Exception(f"音频处理失败: {str(e)}")
    
    def _convert_to_audio(self, file_path: str, file_ext: str) -> str:
        """
        将视频文件转换为音频文件
        
        Args:
            file_path: 源文件路径
            file_ext: 文件扩展名
            
        Returns:
            音频文件路径
        """
        # 如果是视频文件，提取音频
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            logger.info("🎬 检测到视频文件，提取音频...")
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_audio_path = temp_file.name
            
            # 使用moviepy提取音频
            video = VideoFileClip(file_path)
            audio = video.audio
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            audio.close()
            video.close()
            
            logger.info(f"✅ 音频提取完成: {temp_audio_path}")
            return temp_audio_path
        
        # 如果已经是音频文件，检查是否需要格式转换
        elif file_ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']:
            # OpenAI Whisper支持这些格式，直接返回
            return file_path
        
        else:
            # 尝试用pydub转换
            logger.info(f"🔄 转换音频格式: {file_ext}")
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_audio_path = temp_file.name
            
            audio = AudioSegment.from_file(file_path)
            audio.export(temp_audio_path, format="wav")
            
            logger.info(f"✅ 格式转换完成: {temp_audio_path}")
            return temp_audio_path
    
    def _transcribe_audio(self, audio_path: str) -> str:
        """
        使用OpenAI Whisper进行语音转文字
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            转写文本
        """
        logger.info("🗣️ 开始语音转文字...")
        
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        transcription = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
        logger.info(f"📝 转写结果长度: {len(transcription)} 字符")
        
        return transcription
    
    def _get_audio_duration(self, file_path: str, file_ext: str) -> float:
        """
        获取音频时长（秒）
        
        Args:
            file_path: 文件路径
            file_ext: 文件扩展名
            
        Returns:
            时长（秒）
        """
        try:
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                # 视频文件
                video = VideoFileClip(file_path)
                duration = video.duration
                video.close()
                return duration
            else:
                # 音频文件
                audio = AudioSegment.from_file(file_path)
                return len(audio) / 1000.0  # 转换为秒
        except Exception as e:
            logger.warning(f"⚠️ 无法获取音频时长: {e}")
            return 0.0

    def process_audio_base64(self, base64_data: str, filename: str) -> Dict[str, Any]:
        """
        处理base64编码的音频数据
        
        Args:
            base64_data: base64编码的音频数据
            filename: 文件名
            
        Returns:
            包含转写结果的字典
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
            # 解码base64数据
            audio_data = base64.b64decode(base64_data)
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # 处理音频文件
            result = self.process_audio_file(temp_file_path, filename)
            return result
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path) 