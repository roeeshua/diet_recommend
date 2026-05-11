import requests
import json
import os
import random
from typing import Optional


class LLMService:
    """大模型服务：支持本地 Ollama 和 DeepSeek API 切换"""

    ENGINE = os.getenv('LLM_ENGINE', 'ollama')
    OLLAMA_URL = os.getenv('OLLAMA_URL', '127.0.0.1:11435')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_MODEL = 'deepseek-chat'

    @classmethod
    def chat(cls, prompt: str, system_prompt: str = None) -> Optional[str]:
        """调用大模型，根据 ENGINE 环境变量选择后端"""
        if cls.ENGINE == 'deepseek':
            return cls._call_deepseek(prompt, system_prompt)
        return cls._call_ollama(prompt, system_prompt)

    @classmethod
    def _call_ollama(cls, prompt: str, system_prompt: str = None) -> str:
        """调用本地 Ollama"""
        url = f"{cls.OLLAMA_URL}/api/generate"
        is_structured = any(kw in prompt for kw in ['JSON格式', '只返回JSON', '只返回'])
        payload = {
            "model": cls.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.6 if is_structured else 1.0,
                "top_p": 0.9,
                "num_predict": 1024
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        response = requests.post(url, json=payload, timeout=6000)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()

    @classmethod
    def _call_deepseek(cls, prompt: str, system_prompt: str = None) -> str:
        """调用 DeepSeek API"""
        if not cls.DEEPSEEK_API_KEY:
            return cls._call_ollama(prompt, system_prompt)

        headers = {
            "Authorization": f"Bearer {cls.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        temperature = random.uniform(1, 1.3)
        top_p = random.uniform(0.8, 1.0)

        payload = {
            "model": cls.DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": temperature,
            'top_p': top_p,
            "max_tokens": 1000
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()