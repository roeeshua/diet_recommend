# ============================================
# 饮食推荐系统 - Makefile
# 用法: make <命令>
# 在 WSL2 Ubuntu 中执行
# ============================================

.PHONY: help ollama ollama-stop run-backend run-backend-detach \
        run-frontend run-frontend-detach run-all \
        install init-db stop status clean test logs

# 颜色
GREEN = \033[0;32m
YELLOW = \033[0;33m
CYAN = \033[0;36m
NC = \033[0m

# ---------- 配置（按需修改）----------
# Ollama 端口（Windows 11434 被 VMware 占用，改用 11435）
OLLAMA_PORT = 11435
# Ollama 路径（Windows 本机）
OLLAMA_EXE = C:\\Users\\zhanh\\AppData\\Local\\Programs\\Ollama\\ollama.exe
# WSL 中访问 Windows 的网关 IP（通常固定）
MYSQL_HOST_WSL = 172.29.208.1
# Node.js 22 安装路径（WSL 内）
NODE22_PATH = $$HOME/node22/bin
# 项目路径（WSL 挂载）
BACKEND_DIR = /mnt/d/diet_recommend/backend
FRONTEND_DIR = /mnt/d/diet_recommend/frontend

help:
	@echo "$(GREEN)饮食推荐系统 - Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)快速启动:$(NC)"
	@echo "  make ollama           - 启动 Ollama (Windows)"
	@echo "  make run-backend      - 启动后端 Flask"
	@echo "  make run-frontend     - 启动前端 Vite"
	@echo ""
	@echo "$(YELLOW)安装与配置:$(NC)"
	@echo "  make install          - 安装全部依赖"
	@echo "  make init-db          - 初始化数据库"
	@echo ""
	@echo "$(YELLOW)服务管理:$(NC)"
	@echo "  make stop             - 停止所有服务"
	@echo "  make stop-backend     - 仅停止后端"
	@echo "  make stop-frontend    - 仅停止前端"
	@echo "  make stop-ollama      - 仅停止 Ollama"
	@echo "  make status           - 查看运行状态"
	@echo "  make logs             - 查看后端日志"
	@echo "  make clean            - 清理依赖和缓存"

# ==================== Ollama（在 Windows 本机运行）====================

ollama:
	@echo "$(GREEN) 启动 Ollama 服务（端口: $(OLLAMA_PORT), GPU: RTX 3050 Ti）$(NC)"
	@echo "  按 Ctrl+C 停止 Ollama"
	@echo ""
	cmd.exe /c "tasklist 2>nul | findstr /i ollama.exe >nul" && ( \
		echo "$(YELLOW)  Ollama 已在运行$(NC)" && exit 0 ) || \
		cmd.exe /c "set OLLAMA_HOST=0.0.0.0:$(OLLAMA_PORT) && $(OLLAMA_EXE) serve"

ollama-stop:
	@echo "$(YELLOW)停止 Ollama...$(NC)"
	cmd.exe /c "taskkill /F /IM ollama.exe 2>nul" && \
		echo "$(GREEN)  Ollama 已停止$(NC)" || echo "  Ollama 未运行"

# ==================== 后端 ====================

run-backend:
	@echo "$(GREEN) 启动后端服务...$(NC)"
	cd $(BACKEND_DIR) && . venv/bin/activate && \
		OLLAMA_URL=http://$(MYSQL_HOST_WSL):$(OLLAMA_PORT) python run.py

run-backend-detach:
	@echo "$(GREEN) 后台启动后端...$(NC)"
	cd $(BACKEND_DIR) && . venv/bin/activate && \
		OLLAMA_URL=http://$(MYSQL_HOST_WSL):$(OLLAMA_PORT) \
		nohup python -u run.py > /tmp/backend.log 2>&1 &

# ==================== 前端 ====================

run-frontend:
	@echo "$(GREEN) 启动前端服务...$(NC)"
	export PATH=$(NODE22_PATH):$$PATH && \
		cd $(FRONTEND_DIR) && npx vite --host 0.0.0.0 --port 5173

run-frontend-detach:
	@echo "$(GREEN) 后台启动前端...$(NC)"
	export PATH=$(NODE22_PATH):$$PATH && \
		cd $(FRONTEND_DIR) && \
		nohup npx vite --host 0.0.0.0 --port 5173 > /tmp/frontend.log 2>&1 &

# ==================== 一键启动（提示）====================

run-all:
	@echo "$(YELLOW)========== 启动所有服务 ==========$(NC)"
	@echo ""
	@echo "$(CYAN)方法一（推荐，开三个终端各执行一条）:$(NC)"
	@echo "  终端1: make ollama"
	@echo "  终端2: make run-backend"
	@echo "  终端3: make run-frontend"
	@echo ""
	@echo "$(CYAN)方法二（后台运行）:$(NC)"
	@echo "  make ollama"
	@echo "  make run-backend-detach"
	@echo "  make run-frontend-detach"
	@echo ""
	@echo "$(CYAN)  访问: http://localhost:5173$(NC)"

# ==================== 安装与初始化 ====================

install:
	@echo "$(GREEN) 安装后端依赖...$(NC)"
	cd backend && python3.12 -m venv venv && \
		. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN) 安装前端依赖...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN) 安装完成！$(NC)"

init-db:
	@echo "$(GREEN) 初始化数据库...$(NC)"
	cd $(BACKEND_DIR) && . venv/bin/activate && python scripts/init_db.py
	@echo "$(GREEN) 数据库初始化完成！$(NC)"

# ==================== 服务管理 ====================

stop-backend:
	@echo "$(YELLOW)停止后端...$(NC)"
	fuser -k 5000/tcp 2>/dev/null && echo "  后端已停止" || echo "  后端未运行"

stop-frontend:
	@echo "$(YELLOW)停止前端...$(NC)"
	fuser -k 5173/tcp 2>/dev/null && echo "  前端已停止" || echo "  前端未运行"

stop-ollama:
	@echo "$(YELLOW)停止 Ollama...$(NC)"
	cmd.exe /c "taskkill /F /IM ollama.exe 2>nul" >/dev/null 2>&1 && echo "  Ollama 已停止" || echo "  Ollama 未运行"

stop: stop-backend stop-frontend stop-ollama
	@echo "$(GREEN) 所有服务已停止$(NC)"

status:
	@echo "$(YELLOW)========== 服务状态 ==========$(NC)"
	cmd.exe /c "tasklist 2>nul | findstr /i ollama.exe >nul" >/dev/null 2>&1 && \
		echo "  Ollama:   $(GREEN)运行中$(NC)" || echo "  Ollama:   $(YELLOW)未运行$(NC)"
	curl -s --connect-timeout 2 http://localhost:5000/health >/dev/null 2>&1 && \
		echo "  后端:     $(GREEN)运行中$(NC)" || echo "  后端:     $(YELLOW)未运行$(NC)"
	curl -s --connect-timeout 2 http://localhost:5173 >/dev/null 2>&1 && \
		echo "  前端:     $(GREEN)运行中$(NC)" || echo "  前端:     $(YELLOW)未运行$(NC)"
	@echo ""
	@echo "$(YELLOW)GPU 状态:$(NC)"
	cmd.exe /c "nvidia-smi 2>nul | findstr \"RTX\"" 2>/dev/null || true

# ==================== 清理 ====================

clean:
	@echo "$(YELLOW)清理后端缓存...$(NC)"
	rm -rf $(BACKEND_DIR)/venv $(BACKEND_DIR)/__pycache__
	rm -rf $(BACKEND_DIR)/data/embeddings
	@echo "$(YELLOW)清理前端缓存...$(NC)"
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/package-lock.json
	@echo "$(GREEN) 清理完成！$(NC)"

# ==================== 其他 ====================

test:
	@echo "$(GREEN)运行测试...$(NC)"
	cd $(BACKEND_DIR) && . venv/bin/activate && python -m pytest -v || echo "暂无测试用例"

logs:
	@tail -50 /tmp/backend.log 2>/dev/null || echo "  后端日志为空"
