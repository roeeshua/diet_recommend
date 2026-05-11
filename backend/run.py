import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # 只在 Flask reloader 子进程中预热 RAG 模型（避免 PyTorch 阻塞首次请求）
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        import threading
        from app.services.retrieval_service import RetrievalService

        def warmup():
            with app.app_context():
                from app.models.food import Food
                _ = Food.query.first()
                try:
                    RetrievalService.search_by_category("预热")
                    print("✅ RAG 模型已就绪")
                except Exception:
                    print("⚠️ RAG 模型预热失败（将使用关键词回退）")

        threading.Thread(target=warmup, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=True)
