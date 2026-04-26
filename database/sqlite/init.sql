-- YouthMind SQLite数据库初始化脚本
-- 版本: 2.0.0 (SQLite版本)
-- 创建时间: 2024-01-01

-- ============================================
-- 用户相关表
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    nickname TEXT,
    avatar TEXT,
    user_type TEXT NOT NULL DEFAULT 'teen' CHECK(user_type IN ('teen', 'admin')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'banned')),
    last_login_at DATETIME,
    last_login_ip TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 青少年档案表
CREATE TABLE IF NOT EXISTS teen_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    real_name TEXT,
    gender TEXT CHECK(gender IN ('male', 'female', 'other')),
    birth_date DATE,
    school TEXT,
    grade TEXT,
    risk_level TEXT NOT NULL DEFAULT 'green' CHECK(risk_level IN ('green', 'yellow', 'orange', 'red')),
    risk_updated_at DATETIME,
    guardian_phone TEXT,
    emergency_contact TEXT,
    emergency_phone TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_teen_profiles_risk_level ON teen_profiles(risk_level);

-- ============================================
-- 心理测评相关表
-- ============================================

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    question_count INTEGER NOT NULL,
    scoring_rule TEXT,
    interpretation TEXT,
    estimated_time INTEGER,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assessments_code ON assessments(code);
CREATE INDEX IF NOT EXISTS idx_assessments_category ON assessments(category);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL DEFAULT 'single' CHECK(question_type IN ('single', 'multiple', 'scale')),
    options TEXT,
    scoring TEXT,
    reverse_scoring INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    UNIQUE(assessment_id, question_number)
);

CREATE TABLE IF NOT EXISTS assessment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL,
    answers TEXT NOT NULL,
    total_score REAL,
    result_level TEXT,
    result_interpretation TEXT,
    recommendations TEXT,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

CREATE INDEX IF NOT EXISTS idx_assessment_records_user_id ON assessment_records(user_id);

-- ============================================
-- 情绪记录表
-- ============================================

CREATE TABLE IF NOT EXISTS emotion_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    emotion_type TEXT NOT NULL,
    emotion_score REAL NOT NULL,
    source TEXT DEFAULT 'chat' CHECK(source IN ('chat', 'assessment', 'manual')),
    source_id INTEGER,
    context TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_emotion_records_user_id ON emotion_records(user_id);
CREATE INDEX IF NOT EXISTS idx_emotion_records_created_at ON emotion_records(created_at);

-- ============================================
-- 预警相关表
-- ============================================

CREATE TABLE IF NOT EXISTS alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alert_level TEXT NOT NULL CHECK(alert_level IN ('yellow', 'orange', 'red')),
    alert_type TEXT NOT NULL,
    trigger_source TEXT NOT NULL,
    trigger_content TEXT,
    trigger_keywords TEXT,
    risk_score INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'resolved', 'closed')),
    handler_id INTEGER,
    handle_time DATETIME,
    handle_result TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alert_events_user_id ON alert_events(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_events_alert_level ON alert_events(alert_level);
CREATE INDEX IF NOT EXISTS idx_alert_events_status ON alert_events(status);

CREATE TABLE IF NOT EXISTS alert_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_event_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL,
    recipient TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed')),
    sent_at DATETIME,
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_event_id) REFERENCES alert_events(id) ON DELETE CASCADE
);

-- ============================================
-- 内容相关表
-- ============================================

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    category TEXT,
    tags TEXT,
    cover_image TEXT,
    author TEXT,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    is_published INTEGER DEFAULT 0,
    published_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_is_published ON articles(is_published);

CREATE TABLE IF NOT EXISTS audio_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    audio_url TEXT NOT NULL,
    duration INTEGER,
    category TEXT,
    play_count INTEGER DEFAULT 0,
    is_published INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL CHECK(resource_type IN ('article', 'audio')),
    resource_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, resource_type, resource_id)
);

-- ============================================
-- 系统配置表
-- ============================================

CREATE TABLE IF NOT EXISTS system_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_action ON operation_logs(action);

-- ============================================
-- 初始数据
-- ============================================

-- 插入默认管理员账号 (密码: admin123)
INSERT INTO users (phone, password, nickname, user_type, status) VALUES
('admin', '$2b$10$YourHashedPasswordHere', '系统管理员', 'admin', 'active');

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES
('site_name', 'YouthMind', '站点名称'),
('site_description', '青少年心理AI辅导平台', '站点描述'),
('max_message_length', '2000', '消息最大长度'),
('chat_context_messages', '10', '上下文消息数量'),
('alert_red_threshold', '80', '红色预警阈值'),
('alert_orange_threshold', '60', '橙色预警阈值'),
('alert_yellow_threshold', '40', '黄色预警阈值');

-- 插入示例文章
INSERT INTO articles (title, content, summary, category, tags, author, is_published, published_at) VALUES
('如何应对考试焦虑', '考试焦虑是很多同学都会遇到的问题...', '本文介绍了几种缓解考试焦虑的方法', 'anxiety', '考试,焦虑,学习方法', '心理老师', 1, CURRENT_TIMESTAMP),
('建立良好的人际关系', '良好的人际关系对青少年的成长至关重要...', '分享建立良好人际关系的小技巧', 'relationships', '人际关系,社交,沟通', '心理老师', 1, CURRENT_TIMESTAMP);

-- 插入示例音频资源
INSERT INTO audio_resources (title, description, audio_url, duration, category, is_published) VALUES
('放松冥想', '跟随引导进行放松冥想...', '/audio/relaxation.mp3', 600, 'meditation', 1),
('睡前故事', '帮助入睡的舒缓故事...', '/audio/sleep-story.mp3', 900, 'sleep', 1);
