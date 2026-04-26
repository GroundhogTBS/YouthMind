# YouthMind API 使用说明

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3001 | 青少年端界面 |
| 后端API | http://localhost:8000/api | 用户认证、聊天等API |
| AI服务 | http://localhost:9000/docs | 情绪分析、危机检测API |

---

## 后端API (端口 8000)

### 用户相关

#### 注册
```
POST /api/user/register
请求体: { "phone": "手机号", "password": "密码" }
返回: { "accessToken": "令牌", "user": { ... } }
```

#### 登录
```
POST /api/user/login
请求体: { "phone": "手机号", "password": "密码" }
返回: { "accessToken": "令牌", "user": { ... } }
```

#### 获取个人信息
```
GET /api/user/profile
请求头: Authorization: Bearer <令牌>
返回: { "user": { ... }, "profile": { ... } }
```

### 聊天相关

#### 创建会话
```
POST /api/chat/session
请求头: Authorization: Bearer <令牌>
返回: { "id": 1, "userId": 1, ... }
```

#### 发送消息
```
POST /api/chat/send/:sessionId
请求头: Authorization: Bearer <令牌>
请求体: { "content": "消息内容" }
返回: { "userMessage": {...}, "botMessage": {...}, "alert": false }
```

#### 获取会话列表
```
GET /api/chat/sessions
请求头: Authorization: Bearer <令牌>
返回: [ { "id": 1, "title": "标题", ... }, ... ]
```

### 健康检查
```
GET /api/health
返回: { "status": "ok", "service": "youthmind-api" }
```

---

## AI服务 (端口 9000)

### 发送消息获取回复
```
POST /ai/chat/send
请求体: { "session_id": "default", "content": "你好" }
返回: { "content": "回复内容", "emotion": {...}, "alert": false }
```

### 情绪分析
```
POST /ai/emotion/analyze
请求体: { "text": "我今天很开心" }
返回: { "primary_emotion": "happy", "confidence": 0.9 }
```

### 危机检测
```
POST /ai/crisis/detect
请求体: { "text": "我不想活了" }
返回: { "risk_level": "red", "should_alert": true }
```

---

## 使用流程

### 1. 注册/登录
```bash
# 注册新用户
curl -X POST http://localhost:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"123456"}'

# 登录
curl -X POST http://localhost:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"123456"}'
```

### 2. 创建会话并发送消息
```bash
# 创建会话
curl -X POST http://localhost:8000/api/chat/session \
  -H "Authorization: Bearer <你的令牌>"

# 发送消息
curl -X POST http://localhost:8000/api/chat/send/1 \
  -H "Authorization: Bearer <你的令牌>" \
  -H "Content-Type: application/json" \
  -d '{"content":"你好，我想和你聊聊"}'
```

---

## 常见问题

### 1. 401 未授权
- 检查是否已登录
- 检查Authorization头是否正确

### 2. AI服务无响应
- 确认AI服务已启动 (http://localhost:9000/health)
- 检查后端配置的AI_SERVICE_URL是否正确

### 3. 登录后跳转失败
- 检查前端路由配置
- 确认token已正确存储
