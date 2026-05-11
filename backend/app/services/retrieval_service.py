"""向量检索服务 - 实现 RAG 架构的检索阶段

使用 sentence-transformers 将食材编码为语义向量，
根据用户偏好和画像进行语义检索，替代全量食材投喂。
"""

import json
import os
import importlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from ..models.food import Food

# 标记：sentence-transformers 采用延迟导入，避免模块加载时卡死
_HAS_SENTENCE_TRANSFORMERS = None  # None=未检测, True/False=检测结果


class RetrievalService:
    """向量检索服务"""

    # 缓存目录（backend/data/embeddings/）
    CACHE_DIR = Path(__file__).resolve().parent.parent.parent / 'data' / 'embeddings'

    # 各类别检索数量配置（确保三餐多样性和营养均衡）
    CATEGORY_TOP_K: Dict[str, int] = {
        '主食': 5,
        '蛋白质': 7,
        '蔬菜': 7,
        '水果': 4,
        '家常菜': 6,
        '汤类': 3,
    }
    DEFAULT_TOP_K = 3  # 未匹配类别的默认值

    _encoder: Optional['SentenceTransformer'] = None
    _food_ids: Optional[List[int]] = None
    _food_embeddings: Optional[np.ndarray] = None

    # ======================== 编码器管理 ========================

    @classmethod
    def _check_sentence_transformers(cls) -> bool:
        """检测 sentence-transformers 是否可用（只检测一次，不触发 PyTorch 加载）"""
        global _HAS_SENTENCE_TRANSFORMERS
        if _HAS_SENTENCE_TRANSFORMERS is None:
            _HAS_SENTENCE_TRANSFORMERS = importlib.util.find_spec("sentence_transformers") is not None
        return _HAS_SENTENCE_TRANSFORMERS

    @classmethod
    def _get_encoder(cls) -> 'SentenceTransformer':
        """延迟加载编码模型（首次调用时下载）"""
        if cls._encoder is None:
            if not cls._check_sentence_transformers():
                raise RuntimeError(
                    "sentence-transformers 未安装，无法使用语义检索。"
                    "请执行: pip install sentence-transformers"
                )
            os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
            from sentence_transformers import SentenceTransformer
            model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
            model_path = os.path.expanduser(
                '~/.cache/huggingface/hub/'
                'models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/'
                'snapshots/e8f8c211226b894fcb81acc59f3b34ba3efd5f42'
            )
            if os.path.exists(os.path.join(model_path, 'model.safetensors')):
                cls._encoder = SentenceTransformer(model_path)
            else:
                print(f"📥 首次使用，正在下载语义编码模型 {model_name}...（后续使用将自动缓存）")
                cls._encoder = SentenceTransformer(model_name)
        return cls._encoder

    # ======================== 文本构建 ========================

    @classmethod
    def _build_food_text(cls, food: Food) -> str:
        """将食材转为语义检索文本"""
        features = '、'.join(food.features or [])
        tags = food.tags if isinstance(food.tags, str) else ('、'.join(food.tags) if food.tags else '')
        return (
            f"{food.name}。"
            f"类别：{food.category}。"
            f"每100克{food.calories}卡路里。"
            f"标签：{tags}。"
            f"饮食特征：{features}。"
            f"适宜季节：{food.season}。"
        )

    # ======================== 向量缓存管理 ========================

    @classmethod
    def _get_cache_paths(cls):
        """获取缓存文件路径"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CACHE_DIR / 'food_ids.json', cls.CACHE_DIR / 'embeddings.npy'

    @classmethod
    def _load_cache(cls):
        """尝试从磁盘加载缓存的向量"""
        ids_path, emb_path = cls._get_cache_paths()
        if not ids_path.exists() or not emb_path.exists():
            return None, None
        with open(ids_path, 'r', encoding='utf-8') as f:
            food_ids = json.load(f)
        embeddings = np.load(str(emb_path))
        return food_ids, embeddings

    @classmethod
    def _save_cache(cls, food_ids: List[int], embeddings: np.ndarray):
        """将向量缓存到磁盘"""
        ids_path, emb_path = cls._get_cache_paths()
        with open(ids_path, 'w', encoding='utf-8') as f:
            json.dump(food_ids, f)
        np.save(str(emb_path), embeddings)
        print(f"📦 已缓存 {len(food_ids)} 条食材向量到 {cls.CACHE_DIR}")

    @classmethod
    def _ensure_embeddings(cls):
        """确保食材向量已加载（优先级：内存缓存 > 磁盘缓存 > 重新计算）"""
        food_count = Food.query.count()
        if food_count == 0:
            cls._food_ids = []
            cls._food_embeddings = np.array([])
            return

        # 内存缓存有效
        if cls._food_ids is not None and cls._food_embeddings is not None:
            if len(cls._food_ids) == food_count:
                return

        # 磁盘缓存有效
        cached_ids, cached_emb = cls._load_cache()
        if cached_ids is not None and len(cached_ids) == food_count:
            cls._food_ids = cached_ids
            cls._food_embeddings = cached_emb
            print(f"📖 从缓存加载 {len(cached_ids)} 条食材向量")
            return

        # 重新编码
        cls._compute_embeddings()

    @classmethod
    def _compute_embeddings(cls):
        """计算所有食材的语义向量"""
        foods = Food.query.all()
        if not foods:
            cls._food_ids = []
            cls._food_embeddings = np.array([])
            return

        encoder = cls._get_encoder()
        food_ids = [f.id for f in foods]
        food_texts = [cls._build_food_text(f) for f in foods]

        print(f"🧠 正在编码 {len(foods)} 条食材...")
        embeddings = encoder.encode(food_texts, normalize_embeddings=True, show_progress_bar=True)

        cls._food_ids = food_ids
        cls._food_embeddings = embeddings
        cls._save_cache(food_ids, embeddings)

    # ======================== 核心检索方法 ========================

    @classmethod
    def search(cls, query: str, top_k: int = 8) -> List[dict]:
        """基础语义搜索：返回最相似的 top_k 条食材"""
        if not cls._check_sentence_transformers():
            return cls._fallback_search(query, top_k)

        cls._ensure_embeddings()
        if not cls._food_ids or cls._food_embeddings is None or len(cls._food_embeddings) == 0:
            return []

        try:
            encoder = cls._get_encoder()
        except RuntimeError:
            return cls._fallback_search(query, top_k)

        query_vec = encoder.encode(query, normalize_embeddings=True)
        scores = np.dot(cls._food_embeddings, query_vec)

        top_indices = scores.argsort()[-top_k:][::-1]
        return [Food.query.get(cls._food_ids[i]).to_dict()
                for i in top_indices
                if Food.query.get(cls._food_ids[i])]

    @classmethod
    def search_by_category(cls, query: str, custom_top_k: Optional[Dict[str, int]] = None) -> List[dict]:
        """分类感知的多样化检索：每类取 Top-K，确保多样性

        Args:
            query: 检索查询（用户偏好 + 画像描述等）
            custom_top_k: 自定义各类别检索数量，覆盖默认配置

        Returns:
            合并后的食材列表（已按类别多样化）
        """
        if not cls._check_sentence_transformers():
            return cls._fallback_search(query, sum(cls.CATEGORY_TOP_K.values()))

        cls._ensure_embeddings()
        if not cls._food_ids or cls._food_embeddings is None or len(cls._food_embeddings) == 0:
            return []

        try:
            encoder = cls._get_encoder()
        except RuntimeError:
            return cls._fallback_search(query, sum(cls.CATEGORY_TOP_K.values()))
        config = {**cls.CATEGORY_TOP_K}
        if custom_top_k:
            config.update(custom_top_k)

        # 按类别分组
        category_foods: Dict[str, List[int]] = defaultdict(list)
        category_indices: Dict[str, List[int]] = defaultdict(list)

        for idx, food_id in enumerate(cls._food_ids):
            food = Food.query.get(food_id)
            if food:
                cat = food.category or '未分类'
                category_foods[cat].append(food)
                category_indices[cat].append(idx)

        query_vec = encoder.encode(query, normalize_embeddings=True)

        # 每类取 Top-K
        result = []
        seen_ids = set()

        for cat in category_foods:
            k = config.get(cat, cls.DEFAULT_TOP_K)
            foods = category_foods[cat]
            indices = category_indices[cat]

            food_vecs = cls._food_embeddings[indices]
            scores = np.dot(food_vecs, query_vec)

            top_k = min(k, len(foods))
            top_local = scores.argsort()[-top_k:][::-1]

            for local_idx in top_local:
                food = foods[local_idx]
                if food.id not in seen_ids:
                    result.append(food.to_dict())
                    seen_ids.add(food.id)

        return result

    # ======================== 回退策略 ========================

    @classmethod
    def _fallback_search(cls, query: str, top_k: int = 8) -> List[dict]:
        """当 sentence-transformers 不可用时，使用关键词匹配回退"""
        print("⚠️ 使用关键词匹配回退（建议安装 sentence-transformers 以获得语义检索能力）")
        query_lower = query.lower()

        foods = Food.query.all()
        scored = []
        for food in foods:
            score = 0
            text = cls._build_food_text(food).lower()
            for keyword in query_lower.replace('，', ',').replace('、', ',').split(','):
                keyword = keyword.strip()
                if keyword and keyword in text:
                    score += 1
            if score > 0:
                scored.append((score, food))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [food.to_dict() for _, food in scored[:top_k]]

    # ======================== 管理工具 ========================

    @classmethod
    def clear_cache(cls):
        """清除向量缓存（强制下次重新编码）"""
        ids_path, emb_path = cls._get_cache_paths()
        if ids_path.exists():
            ids_path.unlink()
        if emb_path.exists():
            emb_path.unlink()
        cls._food_ids = None
        cls._food_embeddings = None
        print("🗑️ 向量缓存已清除")
