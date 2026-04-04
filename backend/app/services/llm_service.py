# backend/app/services/llm_service.py
import requests
import json
import os
from typing import Optional

class LLMService:
    """大模型服务：支持本地 Ollama 和 DeepSeek API 切换"""
    
    # 通过环境变量切换：'ollama' 或 'deepseek'
    ENGINE = os.getenv('LLM_ENGINE', 'ollama')  # 默认用本地 Ollama
    
    # Ollama 配置
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2:1.5b')
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_MODEL = 'deepseek-chat'
    
    @classmethod
    def chat(cls, prompt: str, system_prompt: str = None) -> Optional[str]:
        """调用大模型，根据 ENGINE 环境变量选择后端"""
        
        if cls.ENGINE == 'deepseek':
            print("☁️ 使用 DeepSeek API")
            return cls._call_deepseek(prompt, system_prompt)
        else:
            print("🖥️ 使用本地 Ollama")
            return cls._call_ollama(prompt, system_prompt)
    
    @classmethod
    def _call_ollama(cls, prompt: str, system_prompt: str = None) -> str:
        """调用本地 Ollama"""
        url = f"{cls.OLLAMA_URL}/api/generate"
        payload = {
            "model": cls.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 1.3,
                "top_p": 1,
                "num_predict": 512
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()
    
    @classmethod
    def _call_deepseek(cls, prompt: str, system_prompt: str = None) -> str:
        """调用 DeepSeek API"""
        if not cls.DEEPSEEK_API_KEY:
            print("⚠️ 未配置 DEEPSEEK_API_KEY，回退到本地 Ollama")
            return cls._call_ollama(prompt, system_prompt)
        
        headers = {
            "Authorization": f"Bearer {cls.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        import random
        # 随机温度：0.7 到 1.3 之间波动
        temperature = random.uniform(1, 1.3)
    
        # 随机 top_p：0.8 到 1.0 之间波动（越大越多样）
        top_p = random.uniform(0.8, 1.0)

        print(f"🎲 参数: temperature={temperature:.2f}, top_p={top_p:.2f}")
        payload = {
            "model": cls.DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": temperature,
            'top_p': top_p,
            "max_tokens": 1000
        }
        
        payload['messages'] = [m for m in payload['messages'] if m]
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()