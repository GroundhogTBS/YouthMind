// YouthMind MongoDB 初始化脚本
// 版本: 1.0.0
// 创建时间: 2024-01-01

// 切换到 youthmind 数据库
db = db.getSiblingDB('youthmind');

// ============================================
// 会话集合
// ============================================

db.createCollection('sessions', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['userId', 'status'],
            properties: {
                userId: {
                    bsonType: 'long',
                    description: '用户ID，必填'
                },
                title: {
                    bsonType: 'string',
                    description: '会话标题'
                },
                status: {
                    enum: ['active', 'ended', 'archived'],
                    description: '会话状态'
                },
                startTime: {
                    bsonType: 'date',
                    description: '开始时间'
                },
                endTime: {
                    bsonType: 'date',
                    description: '结束时间'
                },
                lastMessageAt: {
                    bsonType: 'date',
                    description: '最后消息时间'
                },
                messageCount: {
                    bsonType: 'int',
                    description: '消息数量'
                },
                summary: {
                    bsonType: 'string',
                    description: '会话摘要'
                },
                emotionAnalysis: {
                    bsonType: 'object',
                    properties: {
                        primaryEmotion: { bsonType: 'string' },
                        emotionScore: { bsonType: 'double' },
                        emotionTrend: { bsonType: 'array' }
                    }
                },
                riskFlags: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'object',
                        properties: {
                            level: { bsonType: 'string' },
                            keyword: { bsonType: 'string' },
                            timestamp: { bsonType: 'date' }
                        }
                    }
                },
                metadata: {
                    bsonType: 'object',
                    description: '元数据'
                },
                createdAt: {
                    bsonType: 'date'
                },
                updatedAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// 会话索引
db.sessions.createIndex({ userId: 1, createdAt: -1 });
db.sessions.createIndex({ status: 1 });
db.sessions.createIndex({ lastMessageAt: -1 });
db.sessions.createIndex({ 'riskFlags.level': 1 });

// ============================================
// 消息集合
// ============================================

db.createCollection('messages', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['sessionId', 'role', 'content'],
            properties: {
                sessionId: {
                    bsonType: 'string',
                    description: '会话ID，必填'
                },
                userId: {
                    bsonType: 'long',
                    description: '用户ID'
                },
                role: {
                    enum: ['user', 'assistant', 'system'],
                    description: '消息角色'
                },
                content: {
                    bsonType: 'string',
                    description: '消息内容'
                },
                contentType: {
                    enum: ['text', 'image', 'audio', 'video'],
                    description: '内容类型'
                },
                emotion: {
                    bsonType: 'object',
                    properties: {
                        type: { bsonType: 'string' },
                        score: { bsonType: 'double' },
                        keywords: { bsonType: 'array' }
                    }
                },
                riskAnalysis: {
                    bsonType: 'object',
                    properties: {
                        level: { bsonType: 'string' },
                        score: { bsonType: 'double' },
                        keywords: { bsonType: 'array' },
                        confidence: { bsonType: 'double' }
                    }
                },
                aiResponse: {
                    bsonType: 'object',
                    properties: {
                        model: { bsonType: 'string' },
                        tokens: {
                            bsonType: 'object',
                            properties: {
                                prompt: { bsonType: 'int' },
                                completion: { bsonType: 'int' },
                                total: { bsonType: 'int' }
                            }
                        },
                        latency: { bsonType: 'int' }
                    }
                },
                feedback: {
                    bsonType: 'object',
                    properties: {
                        rating: { bsonType: 'int' },
                        comment: { bsonType: 'string' },
                        createdAt: { bsonType: 'date' }
                    }
                },
                metadata: {
                    bsonType: 'object'
                },
                createdAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// 消息索引
db.messages.createIndex({ sessionId: 1, createdAt: 1 });
db.messages.createIndex({ userId: 1, createdAt: -1 });
db.messages.createIndex({ role: 1 });
db.messages.createIndex({ 'emotion.type': 1 });
db.messages.createIndex({ 'riskAnalysis.level': 1 });
db.messages.createIndex({ createdAt: -1 });

// ============================================
// 知识库集合
// ============================================

db.createCollection('knowledge_base', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['title', 'content', 'category'],
            properties: {
                title: {
                    bsonType: 'string',
                    description: '标题'
                },
                content: {
                    bsonType: 'string',
                    description: '内容'
                },
                category: {
                    bsonType: 'string',
                    description: '分类'
                },
                tags: {
                    bsonType: 'array',
                    items: { bsonType: 'string' }
                },
                embedding: {
                    bsonType: 'array',
                    items: { bsonType: 'double' },
                    description: '向量嵌入'
                },
                embeddingModel: {
                    bsonType: 'string',
                    description: '嵌入模型'
                },
                source: {
                    bsonType: 'string',
                    description: '来源'
                },
                isActive: {
                    bsonType: 'bool',
                    description: '是否启用'
                },
                viewCount: {
                    bsonType: 'int',
                    description: '查看次数'
                },
                createdAt: {
                    bsonType: 'date'
                },
                updatedAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// 知识库索引
db.knowledge_base.createIndex({ category: 1 });
db.knowledge_base.createIndex({ tags: 1 });
db.knowledge_base.createIndex({ isActive: 1 });
db.knowledge_base.createIndex({ createdAt: -1 });

// ============================================
// 对话模板集合
// ============================================

db.createCollection('chat_templates', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['name', 'category', 'content'],
            properties: {
                name: {
                    bsonType: 'string',
                    description: '模板名称'
                },
                category: {
                    bsonType: 'string',
                    description: '分类'
                },
                description: {
                    bsonType: 'string',
                    description: '描述'
                },
                content: {
                    bsonType: 'string',
                    description: '模板内容'
                },
                variables: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'object',
                        properties: {
                            name: { bsonType: 'string' },
                            type: { bsonType: 'string' },
                            required: { bsonType: 'bool' },
                            defaultValue: { bsonType: 'string' }
                        }
                    }
                },
                isActive: {
                    bsonType: 'bool'
                },
                usageCount: {
                    bsonType: 'int'
                },
                createdAt: {
                    bsonType: 'date'
                },
                updatedAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// 对话模板索引
db.chat_templates.createIndex({ category: 1 });
db.chat_templates.createIndex({ isActive: 1 });

// ============================================
// 用户行为日志集合
// ============================================

db.createCollection('user_behavior_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['userId', 'action'],
            properties: {
                userId: {
                    bsonType: 'long',
                    description: '用户ID'
                },
                action: {
                    bsonType: 'string',
                    description: '行为类型'
                },
                resourceType: {
                    bsonType: 'string',
                    description: '资源类型'
                },
                resourceId: {
                    bsonType: 'string',
                    description: '资源ID'
                },
                details: {
                    bsonType: 'object',
                    description: '详情'
                },
                deviceInfo: {
                    bsonType: 'object',
                    properties: {
                        platform: { bsonType: 'string' },
                        os: { bsonType: 'string' },
                        browser: { bsonType: 'string' },
                        screenWidth: { bsonType: 'int' },
                        screenHeight: { bsonType: 'int' }
                    }
                },
                location: {
                    bsonType: 'object',
                    properties: {
                        ip: { bsonType: 'string' },
                        city: { bsonType: 'string' },
                        province: { bsonType: 'string' }
                    }
                },
                sessionId: {
                    bsonType: 'string',
                    description: '会话ID'
                },
                duration: {
                    bsonType: 'int',
                    description: '持续时间(毫秒)'
                },
                createdAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// 行为日志索引
db.user_behavior_logs.createIndex({ userId: 1, createdAt: -1 });
db.user_behavior_logs.createIndex({ action: 1 });
db.user_behavior_logs.createIndex({ createdAt: -1 }, { expireAfterSeconds: 7776000 }); // TTL: 90天

// ============================================
// AI模型调用日志集合
// ============================================

db.createCollection('ai_model_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['model', 'service'],
            properties: {
                model: {
                    bsonType: 'string',
                    description: '模型名称'
                },
                service: {
                    bsonType: 'string',
                    description: '服务名称'
                },
                userId: {
                    bsonType: 'long'
                },
                sessionId: {
                    bsonType: 'string'
                },
                input: {
                    bsonType: 'object',
                    description: '输入参数'
                },
                output: {
                    bsonType: 'object',
                    description: '输出结果'
                },
                tokens: {
                    bsonType: 'object',
                    properties: {
                        prompt: { bsonType: 'int' },
                        completion: { bsonType: 'int' },
                        total: { bsonType: 'int' }
                    }
                },
                latency: {
                    bsonType: 'int',
                    description: '延迟(毫秒)'
                },
                status: {
                    enum: ['success', 'failed'],
                    description: '状态'
                },
                errorMessage: {
                    bsonType: 'string'
                },
                cost: {
                    bsonType: 'double',
                    description: '成本'
                },
                createdAt: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// AI模型日志索引
db.ai_model_logs.createIndex({ model: 1, createdAt: -1 });
db.ai_model_logs.createIndex({ service: 1 });
db.ai_model_logs.createIndex({ userId: 1 });
db.ai_model_logs.createIndex({ createdAt: -1 }, { expireAfterSeconds: 2592000 }); // TTL: 30天

// ============================================
// 初始数据
// ============================================

// 插入默认对话模板
db.chat_templates.insertMany([
    {
        name: '共情回应模板',
        category: 'empathy',
        description: '用于表达共情和理解',
        content: '我能感受到你现在{{emotion}}的心情。{{situation}}确实让人感到{{feeling}}。你愿意和我多说说吗？',
        variables: [
            { name: 'emotion', type: 'string', required: true },
            { name: 'situation', type: 'string', required: true },
            { name: 'feeling', type: 'string', required: true }
        ],
        isActive: true,
        usageCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    },
    {
        name: '危机干预模板',
        category: 'crisis',
        description: '用于危机情况下的回应',
        content: '我非常关心你的安全。如果你现在感到非常痛苦，请记住：\n1. 你不是一个人\n2. 这种感觉是可以改变的\n3. 有很多人愿意帮助你\n\n如果你愿意，可以拨打以下热线：\n- 全国心理援助热线：400-161-9995\n- 北京心理危机研究与干预中心：010-82951332',
        variables: [],
        isActive: true,
        usageCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    },
    {
        name: '情绪引导模板',
        category: 'guidance',
        description: '用于引导用户表达情绪',
        content: '听起来你最近经历了一些让你感到{{emotion}}的事情。能告诉我具体发生了什么吗？我在这里倾听。',
        variables: [
            { name: 'emotion', type: 'string', required: true }
        ],
        isActive: true,
        usageCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    }
]);

// 插入知识库示例
db.knowledge_base.insertMany([
    {
        title: '什么是焦虑',
        content: '焦虑是一种正常的情绪反应，是对未来不确定性的担忧。适度的焦虑可以帮助我们更好地应对挑战，但过度的焦虑可能影响日常生活。常见的焦虑症状包括：心跳加速、出汗、坐立不安、难以集中注意力等。',
        category: 'emotion_knowledge',
        tags: ['焦虑', '情绪', '心理健康'],
        isActive: true,
        viewCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    },
    {
        title: '如何应对学习压力',
        content: '学习压力是青少年常见的困扰。以下是一些应对方法：\n1. 制定合理的学习计划，分解大目标\n2. 保证充足的睡眠和运动\n3. 学会放松技巧，如深呼吸、冥想\n4. 与信任的人交流你的感受\n5. 适当休息，避免过度疲劳',
        category: 'coping_strategies',
        tags: ['学习压力', '应对方法', '青少年'],
        isActive: true,
        viewCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    },
    {
        title: '情绪调节技巧',
        content: '情绪调节是一项重要的心理技能。以下是一些有效的方法：\n1. 深呼吸：缓慢深呼吸可以激活副交感神经，帮助平静\n2. 认知重构：尝试从不同角度看待问题\n3. 表达情绪：通过写日记、绘画、运动等方式释放情绪\n4. 正念练习：关注当下，不加评判地观察自己的感受\n5. 寻求支持：与朋友、家人或专业人士交流',
        category: 'coping_strategies',
        tags: ['情绪调节', '技巧', '心理健康'],
        isActive: true,
        viewCount: 0,
        createdAt: new Date(),
        updatedAt: new Date()
    }
]);

print('YouthMind MongoDB 初始化完成!');
