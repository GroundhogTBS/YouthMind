# YouthMind - 青少年心理健康AI服务平台

## 项目概述

YouthMind 是一个专为青少年设计的心理健康AI服务平台，提供智能对话、情绪分析和危机检测功能。

## 技术架构

```
youthmind/
├── frontend/teen-app/              # 前端 uni-app 项目
│   ├── src/
│   │   ├── pages/                  # 页面组件
│   │   │   ├── home/               # 首页
│   │   │   ├── chat/               # 对话页面
│   │   │   ├── assessment/         # 心理测评
│   │   │   ├── resource/           # 学习资源
│   │   │   ├── profile/            # 个人中心
│   │   │   └── auth/               # 登录认证
│   │   ├── stores/                 # Pinia 状态管理
│   │   ├── api/                    # API 请求封装
│   │   ├── styles/                 # 统一样式系统
│   │   └── types/                  # TypeScript 类型定义
│   └── manifest.json
│
├── ai-service/unified-ai-service/  # 后端 AI 服务
│   ├── main.py                     # FastAPI 入口
│   ├── routers/                    # API 路由
│   │   ├── chat.py                 # 对话接口
│   │   ├── emotion.py              # 情绪分析接口
│   │   └── crisis.py               # 危机检测接口
│   ├── services/                   # 核心服务
│   │   ├── chat_generator.py       # 对话生成
│   │   ├── emotion_analyzer.py     # 情绪分析
│   │   └── crisis_detector.py      # 危机检测
│   ├── models/                     # 数据模型
│   ├── core/                       # 核心配置
│   │   ├── config.py               # 环境配置
│   │   ├── constants.py            # 常量定义
│   │   ├── middleware.py           # 中间件
│   │   ├── auth.py                 # 认证模块
│   │   └── metrics.py              # Prometheus 指标
│   └── tests/                      # 测试文件
│
└── youthmind-res/                  # 资料文档
```

## 核心功能

### 1. 智能对话
- 支持 OpenAI GPT 模型
- 流式响应输出
- 本地回退模式
- 会话历史管理

### 2. 情绪分析
- 9种情绪类型识别
- 程度词加权处理
- 否定词处理
- 情绪趋势分析

### 3. 危机检测
- 四级风险评估（绿/黄/橙/红）
- 即时干预建议
- 心理援助资源推荐
- 危机事件记录

### 4. 心理测评
- 多种专业量表
- 自动评分系统
- 结果分析报告

### 5. 学习资源
- 分类资源库
- 搜索功能
- 阅读统计

## API 接口

### 对话接口
- `POST /ai/chat/send` - 发送消息
- `POST /ai/chat/generate` - 生成回复
- `POST /ai/chat/stream` - 流式输出
- `POST /ai/chat/session` - 创建会话
- `GET /ai/chat/sessions` - 获取会话列表
- `GET /ai/chat/history/{session_id}` - 获取历史

### 情绪分析
- `POST /ai/emotion/analyze` - 分析情绪
- `POST /ai/emotion/batch` - 批量分析
- `GET /ai/emotion/supported` - 支持的情绪类型

### 危机检测
- `POST /ai/crisis/detect` - 检测风险
- `GET /ai/crisis/resources` - 获取援助资源
- `GET /ai/crisis/risk-levels` - 风险等级说明

## 快速开始

### 后端启动
```bash
cd ai-service/unified-ai-service
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd frontend/teen-app
npm install
npm run dev
```

## 环境配置

创建 `.env` 文件：
```
ENVIRONMENT=development
DEBUG=true
PORT=9000

OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-3.5-turbo

DATABASE_URL=sqlite:///./youthmind.db
JWT_SECRET_KEY=your-secret-key
```

## 测试

```bash
cd ai-service/unified-ai-service
pytest tests/ -v
```

## 项目特点

1. **专业性** - 基于青少年心理健康专业知识构建
2. **安全性** - 完善的危机检测和干预机制
3. **可扩展** - 模块化设计，易于扩展
4. **高性能** - 支持流式响应和缓存
5. **易维护** - 统一的代码风格和完善的文档

## 心理援助资源

- 全国心理援助热线：400-161-9995
- 北京心理危机研究与干预中心：010-82951332
- 青少年心理热线：12355

## 许可证

MIT License
