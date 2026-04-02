# ============================================
# 饮食推荐系统 - Makefile
# 用法: make <命令>
# ============================================

.PHONY: help install run-backend run-frontend run-all stop clean test

# 颜色输出
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

help:
	@echo "$(GREEN)饮食推荐系统 Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)可用命令:$(NC)"
	@echo "  make install        - 安装后端和前端依赖"
	@echo "  make run-backend    - 启动后端服务 (Flask)"
	@echo "  make run-frontend   - 启动前端服务 (Vue)"
	@echo "  make run-all        - 同时启动前后端 (需要两个终端)"
	@echo "  make stop           - 停止所有服务"
	@echo "  make clean          - 清理依赖和缓存"
	@echo "  make test           - 运行测试"
	@echo "  make init-db        - 初始化数据库"
	@echo "  make status         - 查看服务状态"

# 安装依赖
install:
	@echo "$(GREEN)安装后端依赖...$(NC)"
	cd backend && python3 -m venv venv && \
		. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)安装前端依赖...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)安装完成！$(NC)"

# 启动后端
run-backend:
	@echo "$(GREEN)启动后端服务...$(NC)"
	cd backend && . venv/bin/activate && python run.py

# 启动前端
run-frontend:
	@echo "$(GREEN)启动前端服务...$(NC)"
	cd frontend && npm run dev

# 同时启动（需要两个终端窗口，这里只提示）
run-all:
	@echo "$(YELLOW)请打开两个终端分别执行:$(NC)"
	@echo "  终端1: make run-backend"
	@echo "  终端2: make run-frontend"

# 初始化数据库
init-db:
	@echo "$(GREEN)初始化数据库...$(NC)"
	cd backend && . venv/bin/activate && python scripts/init_db.py
	@echo "$(GREEN)数据库初始化完成！$(NC)"

# 停止服务
stop:
	@echo "$(YELLOW)停止服务...$(NC)"
	-pkill -f "python run.py" 2>/dev/null || true
	-pkill -f "npm run dev" 2>/dev/null || true
	-pkill -f "vite" 2>/dev/null || true
	@echo "$(GREEN)服务已停止$(NC)"

# 清理依赖和缓存
clean:
	@echo "$(YELLOW)清理后端缓存...$(NC)"
	cd backend && rm -rf venv __pycache__ */__pycache__ */*/__pycache__
	@echo "$(YELLOW)清理前端缓存...$(NC)"
	cd frontend && rm -rf node_modules package-lock.json
	@echo "$(GREEN)清理完成！$(NC)"

# 查看状态
status:
	@echo "$(YELLOW)服务状态:$(NC)"
	@ps aux | grep -E "(python run.py|vite)" | grep -v grep || echo "  没有运行中的服务"

# 测试
test:
	@echo "$(GREEN)运行测试...$(NC)"
	cd backend && . venv/bin/activate && python -m pytest -v || echo "暂无测试用例"