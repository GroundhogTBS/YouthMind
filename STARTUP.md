# YouthMind 项目启动指南

## 项目架构

```
youthmind/
├── frontend/teen-app/          # 前端应用 (端口 3001)
├── ai-service/                 # AI服务 (端口 9000)
│   └── unified-ai-service/
├── backend/api/                # 后端API服务 (端口 8000)
└── database/                   # 数据库脚本
```

## 📋 环境要求

| 工具 | 版本要求 |
|------|---------|
| Node.js | >= 18.0.0 |
| npm | >= 9.0.0 |
| Python | >= 3.10 |

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```bash
# Windows
双击运行 start-all.bat

# 或在项目根目录执行
.\start-all.bat
```

### 方式二：手动启动

#### 第一步：启动 AI 服务

```bash
cd c:\Users\张昕宇\youthmind\ai-service\unified-ai-service

# 创建虚拟环境（首次）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖（首次）
pip install -r requirements.txt

# 启动服务
python main.py
```

#### 第二步：启动后端服务

```bash
cd c:\Users\张昕宇\youthmind\backend\api

# 安装依赖（首次）
npm install

# 启动服务
npm run start:dev
```

#### 第三步：启动前端

```bash
cd c:\Users\张昕宇\youthmind\frontend\teen-app
npm run dev
```

---

## 📝 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3001 | 青少年端界面 |
| 后端API | http://localhost:8000/api | 统一API服务 |
| AI服务 | http://localhost:9000/docs | 情绪分析/危机检测API |

---

## ✅ 验证服务

### 检查服务健康状态

```bash
# 后端API
curl http://localhost:8000/api/health

# AI服务
curl http://localhost:9000/health
```

---

## 🔍 常见问题

### 1. 端口被占用

```bash
# Windows 查看端口占用
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <进程ID> /F
```

### 2. npm install 失败

```bash
# 清除缓存
npm cache clean --force

# 使用国内镜像
npm config set registry https://registry.npmmirror.com
```

### 3. Python 依赖安装失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📞 获取帮助

如有问题，请检查：
1. 各服务日志输出
2. 端口占用情况
3. 环境变量配置
