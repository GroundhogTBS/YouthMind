# YouthMind - 青少年心理健康AI服务平台

## 项目概述

YouthMind 是一个专为12-18岁青少年设计的心理健康AI服务平台，提供24小时智能陪伴、情绪分析和危机干预功能。

## 技术架构

```
youthmind/
├── ai-service/unified-ai-service/  # 统一后端服务 (FastAPI)
│   ├── main.py                     # 服务入口
│   ├── routers/                    # API路由
│   │   ├── chat.py                 # 对话接口
│   │   ├── emotion.py              # 情绪分析接口
│   │   ├── crisis.py               # 危机检测接口
│   │   ├── user.py                 # 用户接口
│   │   ├── assessment.py           # 心理测评接口
│   │   ├── admin.py                # 管理后台接口
│   │   └── ...
│   ├── services/                   # 核心服务
│   │   ├── chat_generator.py       # 对话生成
│   │   ├── emotion_analyzer.py     # 情绪分析
│   │   └── crisis_detector.py      # 危机检测
│   ├── models/                     # 数据模型
│   ├── core/                       # 核心配置
│   │   ├── config.py               # 环境配置
│   │   ├── constants.py            # 常量定义
│   │   ├── middleware.py           # 中间件
│   │   └── auth.py                 # 认证模块
│   ├── data/                       # 外置数据文件
│   │   ├── crisis_keywords.json    # 危机关键词库
│   │   ├── emotion_keywords.json   # 情绪关键词库
│   │   └── crisis_resources.json   # 危机干预资源
│   └── tests/                      # 测试文件
│
├── frontend/teen-app/              # 青少年端 (UniApp)
│   └── src/
│       ├── pages/                  # 页面组件
│       ├── stores/                 # Pinia状态管理
│       ├── api/                    # API请求封装
│       └── styles/                 # 统一样式系统
│
├── frontend/admin-web/             # 管理后台 (Vue3 + Element Plus)
│   └── src/
│       ├── views/                  # 页面组件
│       ├── api/                    # API请求封装
│       └── router/                 # 路由配置
│
└── database/                       # 数据库脚本
    └── sqlite/                     # SQLite初始化脚本
```

## 核心功能

### 1. 智能对话
- 支持 DeepSeek/OpenAI 双模型
- 流式响应输出
- 会话历史管理
- 敏感词过滤

### 2. 情绪分析
- 9种情绪类型识别（开心、难过、焦虑、生气、恐惧、孤独、迷茫、自卑、平静）
- 程度词加权处理
- 否定词处理
- 情绪趋势分析

### 3. 危机检测
- 四级风险评估（绿/黄/橙/红）
- 即时干预建议
- 心理援助资源推荐
- 危机事件记录与追踪

### 4. 心理测评
- PHQ-9 抑郁自评量表
- GAD-7 焦虑自评量表
- PSS-10 压力感知量表
- 自动评分与结果分析

### 5. 管理后台
- 数据仪表盘
- 预警管理
- 用户管理
- 操作日志

## API 接口

### 对话接口
- `POST /ai/chat/send` - 发送消息
- `POST /ai/chat/stream` - 流式输出
- `GET /ai/chat/sessions` - 获取会话列表
- `GET /ai/chat/history/{session_id}` - 获取历史

### 情绪分析
- `POST /ai/emotion/analyze` - 分析情绪
- `POST /ai/emotion/batch` - 批量分析
- `GET /ai/emotion/trend/{user_id}` - 情绪趋势

### 危机检测
- `POST /ai/crisis/detect` - 检测风险
- `GET /ai/crisis/resources` - 获取援助资源

### 管理接口
- `GET /ai/admin/dashboard` - 仪表盘数据
- `GET /ai/admin/crisis-events` - 危机事件列表
- `PUT /ai/admin/crisis-events/{id}/handle` - 处理危机事件

## 快速开始

### 后端启动
```bash
cd ai-service/unified-ai-service
pip install -r requirements.txt
python main.py
```

### 青少年端启动
```bash
cd frontend/teen-app
npm install
npm run dev:h5
```

### 管理后台启动
```bash
cd frontend/admin-web
npm install
npm run dev
```

## 环境配置

创建 `.env` 文件：
```
ENVIRONMENT=development
DEBUG=true
PORT=9000

DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key

DATABASE_URL=sqlite:///./youthmind.db
JWT_SECRET_KEY=your-secret-key
```

## 风险预警机制

| 等级 | 分数范围 | 处理方式 |
|-----|---------|---------|
| 🔴 红色 | 80-100 | 立即中断AI对话，弹出危机热线，通知管理员 |
| 🟠 橙色 | 60-79 | AI转谨慎模式，48小时内人工回访 |
| 🟡 黄色 | 40-59 | 加强引导，推荐自助资源 |
| 🟢 绿色 | 0-39 | 日常陪伴 |

## 心理援助资源

- 全国心理援助热线：**400-161-9995**
- 北京心理危机研究与干预中心：**010-82951332**
- 青少年心理热线：**12355**
- 生命热线：**400-821-1215**

## 许可证

MIT License
