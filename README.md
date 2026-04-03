# 🍽️ 智能饮食推荐系统

基于 Flask + Vue 3 + MySQL 的个性化饮食推荐平台，集成大模型（Ollama + DeepSeek）实现智能推荐、饮食计划生成与 AI 对话助手。

## 主要功能

- 用户注册/登录（JWT 认证）
- 饮食偏好设置（支持自定义标签）
- 大模型食材推荐 & 饮食计划生成
- 计划库（保存、自定义计划、一键打卡）
- 饮食打卡 & 营养统计（热量 + 六项营养指标趋势图）
- AI 饮食助手（支持用户画像与历史饮食上下文）

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Flask, SQLAlchemy, PyMySQL, JWT |
| 前端 | Vue 3, Element Plus, ECharts, Axios |
| 数据库 | MySQL 8.0 |
| 大模型 | Ollama (本地) + DeepSeek API (云端) |

## 环境要求

- 操作系统：Windows 10/11（推荐 WSL 2）或 Linux/macOS
- 数据库：MySQL 8.0
- Python：3.12+
- Node.js：18+
- Ollama：使用本地模型时需要（可选）

## WSL2 用户特别注意：连接 Windows 的 MySQL

如果你的后端运行在 WSL2 中，而 MySQL 安装在 Windows 上，**不能使用 `localhost`**，需要按以下步骤配置：

### 1. 修改 Windows MySQL 允许远程连接

找到 MySQL 配置文件 `my.ini`（通常在 `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`），在 `[mysqld]` 下添加：
```ini
bind-address = 0.0.0.0
```
然后重启 MySQL 服务。

### 2. 创建允许远程连接的用户

用 Navicat 或命令行连接 Windows MySQL，执行：
```sql
CREATE USER 'root'@'%' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### 3. 获取 WSL 中 Windows 主机的 IP

在 WSL 终端中执行：
```bash
cat /etc/resolv.conf | grep nameserver
```
会输出类似 `nameserver 172.29.208.1`，记下这个 IP。

### 4. 配置 `.env` 使用该 IP

```ini
MYSQL_HOST=172.29.208.1   # 用你查到的 IP
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=diet_recommend
```

### 5. 测试连接

在 WSL 终端执行：
```bash
mysql -h 172.29.208.1 -u root -p
```
能进入 MySQL 命令行说明成功。

> **注意**：WSL2 每次重启后 IP 可能会变，需要重新 `cat /etc/resolv.conf | grep nameserver` 获取新 IP 并更新 `.env`。也可以写脚本自动更新。

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/roeeshua/diet_recommend.git
cd diet_recommend
```

### 2. 一键安装依赖

```bash
make install
```

如果提示 `make: command not found`，先安装 make：
```bash
sudo apt install make   # Ubuntu/Debian
# 或手动安装：cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
# 然后 cd ../frontend && npm install
```

### 3. 配置数据库

首先创建数据库：
```sql
CREATE DATABASE diet_recommend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后配置环境变量：
```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，修改以下配置：
```ini
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=diet_recommend
```

最后初始化数据库：
```bash
make init-db
```

### 4. 启动服务

打开两个终端：

**终端1 - 后端：**
```bash
cd backend
source venv/bin/activate   # Windows: .\venv\Scripts\activate
python run.py
```

**终端2 - 前端：**
```bash
cd frontend
npm run dev
```

浏览器访问 `http://localhost:5173` 即可使用。

## 大模型配置

系统支持两种大模型后端，在 `backend/.env` 中通过 `LLM_ENGINE` 切换。

### 方式一：本地 Ollama（免费，离线可用）

**1. 安装 Ollama**

访问 https://ollama.com 下载安装，或在 WSL 中执行：
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**2. 下载模型**

```bash
# 推荐 tinyllama（速度快，资源占用低）
ollama pull tinyllama

# 或 qwen2:1.5b（中文更好，需要更多算力）
ollama pull qwen2:1.5b
```

**3. 启动 Ollama 服务（重要！需要单独一个终端保持运行）**

```bash
ollama serve
```
看到 `Listening on 127.0.0.1:11434` 表示启动成功。

**4. 配置项目**

修改 `backend/.env`：
```ini
LLM_ENGINE=ollama
OLLAMA_MODEL=tinyllama   # 或 qwen2:1.5b
```

**5. 性能提示**
- `tinyllama`（约 0.5B）：普通电脑流畅运行，响应 5-15 秒
- `qwen2:1.5b`（约 1.5B）：需要较好 CPU，响应 30-60 秒，可能超时
- 如果超时，换 `tinyllama` 或改用 DeepSeek API

### 方式二：DeepSeek API（云端，无需本地算力）

**1. 获取 API Key**

访问 https://platform.deepseek.com/ 注册，新用户送 500 万 tokens。

**2. 配置项目**

修改 `backend/.env`：
```ini
LLM_ENGINE=deepseek
DEEPSEEK_API_KEY=sk-你的API密钥
```

**优势**：无需本地 GPU，任何电脑都能流畅运行，响应 1-3 秒。

## 测试验证

后端启动后，可用以下命令测试：

```bash
# 健康检查
curl http://localhost:5000/health

# 注册用户
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123","age":25,"gender":true,"height":175,"weight":70}'

# 登录
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123"}'
```

## 项目结构

```
diet_recommend/
├── backend/            # Flask 后端
│   ├── app/
│   │   ├── models/     # 数据模型（6张表）
│   │   ├── routes/     # API 路由
│   │   ├── services/   # 业务逻辑
│   │   └── utils/      # 工具函数
│   ├── scripts/        # 数据库初始化
│   ├── .env.example    # 环境变量模板
│   └── requirements.txt
├── frontend/           # Vue 3 前端
├── makefile            # 一键配置
└── README.md
```

## 常见问题

**Q: 本地 Ollama 调用超时怎么办？**
A: 1.5B 模型在普通电脑上可能需要 30-60 秒。解决方案：
- 使用更小的模型：`ollama pull tinyllama`
- 或切换为 DeepSeek API

**Q: 提示 `ModuleNotFoundError`**
A: 重新安装依赖：
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt
```

**Q: 数据库连接失败**
A: 检查：MySQL 是否启动、`.env` 密码是否正确、数据库是否已创建

**Q: 前端无法访问后端**
A: 确认后端已启动在 5000 端口，检查前端 `api/index.js` 中的地址

## 许可证

本项目仅用于学习与毕业设计展示。