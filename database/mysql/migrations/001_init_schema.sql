-- YouthMind 数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS youthmind DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE youthmind;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像',
    signature VARCHAR(200) COMMENT '个性签名',
    age INT DEFAULT 0 COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 聊天会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(100) DEFAULT '新对话' COMMENT '会话标题',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_updated_at (updated_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天会话表';

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色(user/assistant)',
    content TEXT NOT NULL COMMENT '消息内容',
    emotion VARCHAR(50) COMMENT '检测到的情绪',
    emotion_score FLOAT COMMENT '情绪分数',
    risk_level VARCHAR(20) COMMENT '风险等级',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';

-- 情绪记录表
CREATE TABLE IF NOT EXISTS emotion_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    emotion_type VARCHAR(50) NOT NULL COMMENT '情绪类型',
    intensity INT DEFAULT 5 COMMENT '情绪强度(1-10)',
    triggers TEXT COMMENT '触发因素',
    thoughts TEXT COMMENT '想法',
    coping_methods TEXT COMMENT '应对方法',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_emotion_type (emotion_type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='情绪记录表';

-- 测评量表
CREATE TABLE IF NOT EXISTS assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '测评代码',
    name VARCHAR(100) NOT NULL COMMENT '测评名称',
    description TEXT COMMENT '测评描述',
    category VARCHAR(50) COMMENT '分类',
    questions JSON NOT NULL COMMENT '问题列表',
    scoring_rules JSON COMMENT '评分规则',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测评量表';

-- 测评记录表
CREATE TABLE IF NOT EXISTS assessment_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    assessment_id INT NOT NULL COMMENT '测评ID',
    answers JSON NOT NULL COMMENT '答案',
    total_score INT COMMENT '总分',
    result_level VARCHAR(50) COMMENT '结果等级',
    result_interpretation TEXT COMMENT '结果解读',
    recommendations TEXT COMMENT '建议',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_assessment_id (assessment_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测评记录表';

-- 学习资源表
CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '标题',
    description TEXT COMMENT '描述',
    content TEXT COMMENT '内容',
    category VARCHAR(50) COMMENT '分类',
    tags JSON COMMENT '标签',
    cover_image VARCHAR(255) COMMENT '封面图',
    views INT DEFAULT 0 COMMENT '浏览量',
    likes INT DEFAULT 0 COMMENT '点赞数',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_views (views),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习资源表';

-- 用户收藏表
CREATE TABLE IF NOT EXISTS user_favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    resource_id INT NOT NULL COMMENT '资源ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_resource (user_id, resource_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 危机事件记录表
CREATE TABLE IF NOT EXISTS crisis_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '用户ID',
    session_id INT COMMENT '会话ID',
    risk_level VARCHAR(20) NOT NULL COMMENT '风险等级',
    risk_score INT COMMENT '风险分数',
    matched_keywords JSON COMMENT '匹配的关键词',
    actions_taken JSON COMMENT '采取的措施',
    resolved BOOLEAN DEFAULT FALSE COMMENT '是否已解决',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='危机事件记录表';

-- 插入默认测评数据
INSERT INTO assessments (code, name, description, category, questions, scoring_rules) VALUES
('emotion', '情绪状态评估', '了解你最近的情绪状态，发现潜在问题', '情绪管理',
'[{"questionNumber":1,"questionText":"最近一周，你感到心情低落的频率是？","options":["几乎没有","偶尔","有时","经常","几乎每天"]},{"questionNumber":2,"questionText":"你对日常活动的兴趣如何？","options":["和以前一样","稍微减少","明显减少","几乎没兴趣","完全没兴趣"]},{"questionNumber":3,"questionText":"你是否感到精力不足或疲劳？","options":["没有","轻微","中等","严重","非常严重"]},{"questionNumber":4,"questionText":"你的睡眠质量如何？","options":["很好","还可以","不太好","很差","非常差"]},{"questionNumber":5,"questionText":"你是否对未来感到悲观？","options":["从不","偶尔","有时","经常","总是"]}]',
'{"scoringMethod":"sum","levelThresholds":{"normal":5,"mild":10,"moderate":15,"severe":20}}'),

('anxiety', '焦虑程度测试', '评估你的焦虑水平，获取专业建议', '情绪管理',
'[{"questionNumber":1,"questionText":"你是否感到紧张或焦虑？","options":["没有","轻微","中等","严重","非常严重"]},{"questionNumber":2,"questionText":"你是否无法停止或控制担忧？","options":["没有","偶尔","有时","经常","总是"]},{"questionNumber":3,"questionText":"你是否对各种事情过分担忧？","options":["没有","偶尔","有时","经常","总是"]},{"questionNumber":4,"questionText":"你是否难以放松？","options":["没有","偶尔","有时","经常","总是"]},{"questionNumber":5,"questionText":"你是否感到坐立不安？","options":["没有","偶尔","有时","经常","总是"]}]',
'{"scoringMethod":"sum","levelThresholds":{"normal":5,"mild":10,"moderate":15,"severe":20}}'),

('self-esteem', '自信心评估', '了解你的自信程度，提升自我认知', '自我成长',
'[{"questionNumber":1,"questionText":"我对自己感到满意","options":["非常同意","同意","不确定","不同意","非常不同意"]},{"questionNumber":2,"questionText":"我觉得自己有很多优点","options":["非常同意","同意","不确定","不同意","非常不同意"]},{"questionNumber":3,"questionText":"我能和别人一样把事情做好","options":["非常同意","同意","不确定","不同意","非常不同意"]},{"questionNumber":4,"questionText":"我对自己有积极的评价","options":["非常同意","同意","不确定","不同意","非常不同意"]},{"questionNumber":5,"questionText":"我觉得自己是一个有价值的人","options":["非常同意","同意","不确定","不同意","非常不同意"]}]',
'{"scoringMethod":"sum","levelThresholds":{"high":20,"normal":15,"low":10,"veryLow":5}}');

-- 插入默认学习资源
INSERT INTO resources (title, description, content, category, tags) VALUES
('如何应对考试焦虑', '考试前的紧张是正常的，学会这些方法让你更从容', 
'考试焦虑是很多同学都会遇到的问题。以下是一些有效的应对方法：\n\n1. 充分准备：提前复习，制定合理的学习计划\n2. 深呼吸：考试前做几次深呼吸，帮助放松\n3. 积极暗示：告诉自己"我已经准备好了"\n4. 合理作息：保证充足的睡眠\n5. 适度运动：运动可以帮助缓解压力', 
'学习压力', '["考试", "焦虑", "学习方法"]'),

('和朋友吵架了怎么办', '友谊中的冲突可以这样化解，让关系更牢固',
'朋友之间的争吵是很常见的，以下是一些处理建议：\n\n1. 冷静下来：先让情绪平复，避免冲动\n2. 换位思考：尝试理解对方的立场\n3. 主动沟通：找一个合适的时机交流\n4. 真诚道歉：如果自己有错，勇敢承认\n5. 学会原谅：接受道歉，放下过去', 
'人际关系', '["友谊", "沟通", "冲突解决"]'),

('提升自信心的方法', '相信自己，你比想象中更优秀',
'自信是成功的重要基石。以下是一些提升自信的方法：\n\n1. 发现优点：列出自己的优点和成就\n2. 设定小目标：从小事做起，积累成功体验\n3. 积极自我对话：用积极的语言鼓励自己\n4. 学习新技能：不断成长增强自信\n5. 接纳不完美：每个人都有缺点，这很正常', 
'自我成长', '["自信", "成长", "自我认知"]'),

('学会放松：深呼吸练习', '简单的呼吸技巧，帮你缓解紧张情绪',
'深呼吸是一种简单有效的放松方法：\n\n1. 找一个安静的地方坐下或躺下\n2. 慢慢吸气，数到4\n3. 屏住呼吸，数到4\n4. 慢慢呼气，数到4\n5. 重复5-10次\n\n这个方法可以在任何紧张的时候使用，比如考试前、演讲前等。', 
'情绪管理', '["放松", "呼吸", "压力管理"]'),

('如何改善睡眠质量', '好的睡眠是心理健康的基础',
'良好的睡眠对身心健康非常重要：\n\n1. 固定作息：每天同一时间睡觉和起床\n2. 创造环境：保持卧室安静、黑暗、凉爽\n3. 睡前放松：避免使用电子设备\n4. 适度运动：白天运动有助于晚上睡眠\n5. 避免刺激：睡前不要喝咖啡或茶', 
'情绪管理', '["睡眠", "健康", "作息"]');
