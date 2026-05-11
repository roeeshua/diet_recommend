# 🍽️ 智能饮食推荐系统

基于 Flask + Vue 3 + MySQL 的个性化饮食推荐平台，集成 **RAG（检索增强生成）** 架构 + 双大模型引擎（Ollama GPU 本地推理 + DeepSeek API），实现智能推荐、饮食计划生成与 AI 对话助手。

## 主要功能

- **用户注册/登录**（JWT 认证）
- **饮食偏好设置**（100+ 预设标签 + 自定义标签，分口味/食材/菜系/烹饪/健康/忌口等 8 类）
- **RAG 智能食材推荐** — 向量检索 + LLM 生成，不盲目全量投喂
- **AI 饮食计划生成** — 自动生成一日三餐，支持保存/一键打卡
- **饮食打卡 & 营养统计** — 六项营养指标（蛋白质/纤维/维生素/糖/脂肪/钠）+ ECharts 月度趋势图
- **AI 饮食助手** — 支持个人资料/偏好/画像/历史记录作为上下文
- **用户饮食画像** — 基于近 30 天打卡自动计算 24 个饮食特征指标

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | Flask 2.3, SQLAlchemy 2.0, PyMySQL |
| 前端框架 | Vue 3 (Composition API), Element Plus, ECharts, Axios |
| 数据库 | MySQL 8.0 |
| 本地大模型 | **Ollama + Qwen2.5:3B**（GPU CUDA 加速推理） |
| 云端大模型 | DeepSeek API |
| 向量检索 | sentence-transformers（语义编码 + 余弦相似度） |

## 系统架构

```
┌───────────────┐     ┌──────────────────────────────────────┐
│  前端 (Vite)  │────▶│           后端 (Flask)               │
│  :5173        │     │                                      │
└───────────────┘     │  ┌─────────┐  ┌──────────────────┐  │
                      │  │ Routes  │─▶│    Services      │  │
                      │  └─────────┘  │                  │  │
                      │               │  ┌────────────┐  │  │
                      │               │  │ Retrieval  │  │  │
                      │               │  │ Service    │◀─│──│── 向量检索
                      │               │  │ (RAG)      │  │  │
                      │               │  └─────┬──────┘  │  │
                      │               │        │         │  │
                      │               │  ┌──────▼───────┐ │  │
                      │               │  │ LLM Service  │ │  │
                      │               │  │              │ │  │
                      │               │  │ Ollama ◀────│─│──│── Windows Ollama
                      │               │  │ (GPU CUDA)  │ │  │    :11435
                      │               │  │              │ │  │
                      │               │  │ DeepSeek API │ │  │
                      │               │  └──────────────┘ │  │
                      │               └──────────────────┘  │
                      │                                      │
                      │  ┌──────────────┐                    │
                      │  │   MySQL      │                    │
                      │  │   :3306      │                    │
                      │  └──────────────┘                    │
                      └──────────────────────────────────────┘
```

### RAG 检索增强生成流程

```
用户请求 (偏好+画像)
       │
       ▼
┌──────────────────┐
│  检索阶段         │  sentence-transformers 编码
│  向量相似度检索   │  按类别分组取 Top-K
│  Top-28 食材      │  (主食5+蛋白质7+蔬菜7+水果4+家常菜6+汤3)
└────────┬─────────┘
         │  召回食材作为上下文
         ▼
┌──────────────────┐
│  增强阶段         │  结构化 Prompt
│  上下文注入       │  "严格从以下食材中选择..."
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  生成阶段         │  Ollama / DeepSeek
│  LLM 推理        │  生成推荐/计划
│  后处理补全       │  不足时自动从检索结果填充
└──────────────────┘
```

## 环境要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 **+ WSL2 Ubuntu** |
| 数据库 | MySQL 8.0（可运行在 Windows 或 Docker 中）|
| Python | 3.12 |
| Node.js | 20.19+ 或 22.12+（**推荐使用 Node.js 22**）|
| GPU（可选） | NVIDIA 显卡 + CUDA（本地 Ollama 推理用）|
| Ollama（可选） | 使用本地模型时需要 |

### 推荐硬件（本地 Ollama 模式）

| 显卡 | 显存 | 推荐模型 | 推理速度 |
|------|------|---------|---------|
| RTX 3050 Ti | 4GB | Qwen2.5:3B (Q4) | 1-3 秒 |
| RTX 3060+ | 6GB+ | Qwen2.5:7B | 2-5 秒 |
| 无 GPU | 仅 CPU | Qwen2.5:1.5B | 10-30 秒 |

## 快速启动（WSL2 环境）

### 1. 安装子系统依赖

```bash
# 在 WSL2 Ubuntu 中执行
cd /mnt/d/diet_recommend

# 安装 Python 依赖
cd backend && python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 安装 Node.js 22（如果还没有）
# 方式一：使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
nvm install 22

# 方式二：直接下载
curl -sL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz -o /tmp/node.tar.xz
mkdir -p ~/node22 && tar -xJf /tmp/node.tar.xz -C ~/node22 --strip-components=1
export PATH=$HOME/node22/bin:$PATH

# 安装前端依赖
cd frontend && npm install && cd ..
```

### 2. 启动 Ollama（Windows 本机）

Ollama 需要**在 Windows 中运行**（而非 WSL），因为 GPU 直通给 Windows 的 CUDA 驱动。

```bash
# 在 Windows 命令提示符或 PowerShell 中
# 由于端口 11434 被 VMware 占用，使用 11435
set OLLAMA_HOST=0.0.0.0:11435
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
```

```bash
# 或在项目目录中：
make ollama
```

验证 GPU 是否生效（看到 `NVIDIA GeForce RTX 3050` 即成功）：

```bash
curl http://127.0.0.1:11435/api/tags
```

### 3. 拉取本地模型

```bash
ollama pull qwen2.5:3b
```

### 4. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，关键配置：

```ini
# 数据库
MYSQL_HOST=172.29.208.1    # WSL 中访问 Windows MySQL 的网关 IP
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=111
MYSQL_DATABASE=diet_recommend

# 大模型引擎
LLM_ENGINE=ollama           # ollama 或 deepseek

# Ollama 配置（从 WSL 访问 Windows 的 Ollama）
OLLAMA_URL=http://172.29.208.1:11435
OLLAMA_MODEL=qwen2.5:3b

# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-你的API密钥
```

### 5. 初始化数据库

```bash
make init-db
```

### 6. 启动服务

开三个终端：

```bash
# 终端 1：Ollama（Windows）
make ollama

# 终端 2：后端（WSL）
make run-backend

# 终端 3：前端（WSL）
make run-frontend
```

访问 **http://localhost:5173**。

### 一键查看状态

```bash
make status
```

## 大模型配置说明

### 双模型切换

系统通过 `LLM_ENGINE` 环境变量控制使用哪个引擎，**也可在运行中的前端 AI 助手页面实时切换**：

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **Ollama 本地** (qwen2.5:3b) | 免费、离线可用、数据不外传 | 输出质量较低、多样性不足 | 日常简单查询、轻量推荐 |
| **DeepSeek API** | 质量高、上下文长、稳定 | 需要网络、有 API 费用 | 复杂对话、高质量计划生成 |

切换命令：

```bash
# 在 WSL 中
curl -X POST http://localhost:5000/api/ai/switch_model \
  -H "Content-Type: application/json" \
  -d '{"engine":"ollama"}'   # 或 "deepseek"

# 查看当前引擎
curl http://localhost:5000/api/ai/get_model
```

### Ollama GPU 加速

在 RTX 3050 Ti（4GB 显存）上，qwen2.5:3b 模型的推理性能：

| 操作 | 首次加载 | 后续推理 |
|------|---------|---------|
| 饮食推荐（8个食材） | ~5 秒 | 1-2 秒 |
| 饮食计划（三餐） | ~8 秒 | 2-4 秒 |
| AI 对话 | ~5 秒 | 1-3 秒 |

### DeepSeek API

注册获取 API Key：https://platform.deepseek.com/

```ini
LLM_ENGINE=deepseek
DEEPSEEK_API_KEY=sk-你的API密钥
```

## 项目结构

```
diet_recommend/
├── backend/                  # Flask 后端
│   ├── app/
│   │   ├── models/           # 6 张数据表
│   │   │   ├── user.py
│   │   │   ├── food.py
│   │   │   ├── user_meal.py
│   │   │   ├── user_plan.py
│   │   │   ├── user_profile.py  # 24 个饮食特征画像
│   │   │   └── preference.py
│   │   ├── routes/           # 9 个 API 蓝图
│   │   ├── services/
│   │   │   ├── retrieval_service.py  # RAG 向量检索服务
│   │   │   ├── llm_service.py        # 双模型 LLM 网关
│   │   │   ├── recommend_service.py  # 推荐引擎（RAG）
│   │   │   ├── plan_service.py       # 饮食计划（RAG）
│   │   │   ├── profile_service.py    # 画像计算
│   │   │   ├── checkin_service.py    # 打卡服务
│   │   │   ├── statistics_service.py # 营养统计
│   │   │   └── ... 
│   │   └── utils/
│   ├── scripts/init_db.py    # 数据库初始化（200+条食材）
│   └── .env                  # 环境配置
├── frontend/                 # Vue 3 前端
│   └── src/
│       ├── views/            # 登录/注册/主页
│       └── components/       # 8 个功能组件
├── makefile                  # 一键管理
└── README.md
```

## API 概览

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/register` | 注册 |
| POST | `/api/login` | 登录 |
| GET | `/api/foods` | 获取食材列表 |
| GET | `/api/recommend/<user_id>` | RAG 饮食推荐 |
| POST | `/api/plan/generate` | AI 生成饮食计划 |
| POST | `/api/plan/save` | 保存计划 |
| POST | `/api/checkin` | 饮食打卡 |
| GET | `/api/statistics/<user_id>/<date>` | 每日营养统计 |
| GET | `/api/statistics/<user_id>/monthly` | 月度趋势 |
| POST | `/api/ai/chat` | AI 对话 |
| POST | `/api/ai/switch_model` | 切换大模型引擎 |
| GET | `/api/profile/<user_id>` | 用户饮食画像 |

## 常见问题

**Q: Ollama 报端口被占用？**
A: 默认 11434 被占用，代码已改为 11435。检查端口：`netstat -ano | findstr :11435`

**Q: WSL 连不上 Windows Ollama？**
A: 确保 Ollama 在 Windows 中已启动且绑定 0.0.0.0。从 WSL 测试：`curl http://172.29.208.1:11435/api/tags`

**Q: 本地模型回复质量差？**
A: Qwen2.5:3B 是 3B 小模型，回复质量和多样性不如 DeepSeek API。建议复杂对话切换至 DeepSeek。

**Q: `ModuleNotFoundError: No module named 'sentence_transformers'`**
A: RAG 向量检索功能可选，缺少该库会自动回退到关键词匹配。如需完整功能：`pip install sentence-transformers`

**Q: GPU 不工作？**
A: 运行 `nvidia-smi` 查看状态。确保 NVIDIA 驱动已安装（不低于 545 版本），Ollama 会自动检测 CUDA。

## 许可证

本项目仅用于学习与毕业设计展示。
