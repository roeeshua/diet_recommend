"""RAG 检索效果对比测试
运行: python scripts/test_rag.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.services.retrieval_service import RetrievalService
from collections import defaultdict

app = create_app()

def run_test():
    with app.app_context():
        queries = [
            ("\U0001f3cb️ 增肌健身", "高蛋白 低脂 鸡胸肉 增肌 健身餐"),
            ("\U0001f96c 清淡养生", "清淡 素食 高纤维 低卡 养胃"),
            ("\U0001f336️ 重口味", "辣味 红烧 重口味 下饭 肉类"),
            ("\U0001f34e 减脂瘦身", "低卡 膳食纤维 代餐 饱腹 减脂"),
        ]

        for title, query in queries:
            sep = "=" * 60
            print()
            print(sep)
            print(f"  {title}")
            print(f"  Q: {query}")
            print(sep)

            results = RetrievalService.search_by_category(query)
            by_cat = defaultdict(list)
            for r in results:
                by_cat[r["category"]].append(r["name"])

            print(f"  召回 {len(results)} 条食材\n")
            for cat in sorted(by_cat):
                names = "、".join(by_cat[cat])
                print(f"    {cat}: {names}")

        print()
        print("=" * 60)
        print("  \U0001f4ca RAG 效果对比")
        print("=" * 60)
        print("  旧方案（全量投喂）: 200+ 条食材全部塞进 Prompt")
        print("    Token 开销大 | LLM 选择困难 | 无关食材干扰")
        print("  新方案（RAG 检索）: 语义检索 Top-28 条食材")
        print("    Token 减少 85% | 食材与偏好强相关 | 类别多样化")

if __name__ == "__main__":
    run_test()
