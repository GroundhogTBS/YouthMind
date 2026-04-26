<template>
  <view class="emotion-page">
    <view class="header">
      <text class="title">今天心情如何？</text>
    </view>

    <view class="emotion-selector">
      <view 
        v-for="emotion in emotions" 
        :key="emotion.type"
        class="emotion-item"
        :class="{ active: selectedEmotion === emotion.type }"
        @click="selectEmotion(emotion.type)"
      >
        <view class="emotion-icon-wrapper">
          <text class="emotion-icon-text">{{ emotion.icon }}</text>
        </view>
        <text class="emotion-label">{{ emotion.label }}</text>
      </view>
    </view>

    <view class="intensity-section" v-if="selectedEmotion">
      <text class="section-title">情绪强度</text>
      <slider 
        :value="intensity" 
        :min="1" 
        :max="10" 
        :step="1"
        @change="onIntensityChange"
        show-value
        activeColor="#6366f1"
        backgroundColor="#e5e7eb"
      />
      <view class="intensity-labels">
        <text>轻微</text>
        <text>强烈</text>
      </view>
    </view>

    <view class="form-section" v-if="selectedEmotion">
      <view class="form-item">
        <text class="form-label">发生了什么？</text>
        <textarea 
          v-model="triggers"
          placeholder="描述一下触发你情绪的事情..."
          class="form-textarea"
        />
      </view>

      <view class="form-item">
        <text class="form-label">当时的想法</text>
        <textarea 
          v-model="thoughts"
          placeholder="你当时在想什么？"
          class="form-textarea"
        />
      </view>

      <view class="form-item">
        <text class="form-label">你是怎么应对的？</text>
        <textarea 
          v-model="copingMethods"
          placeholder="你做了什么来调节情绪？"
          class="form-textarea"
        />
      </view>
    </view>

    <button class="submit-btn" @click="submitRecord" :disabled="!selectedEmotion">
      保存记录
    </button>

    <view class="history-section">
      <text class="section-title">最近记录</text>
      <view class="history-list">
        <view 
          v-for="record in recentRecords" 
          :key="record.id" 
          class="history-item"
        >
          <view class="history-header">
            <view class="history-emotion-wrapper">
              <text class="history-emotion-text">{{ getEmotionIcon(record.emotionType) }}</text>
            </view>
            <text class="history-type">{{ record.emotionType }}</text>
            <text class="history-intensity">强度: {{ record.intensity }}</text>
          </view>
          <text class="history-time">{{ formatTime(record.recordedAt) }}</text>
          <text class="history-trigger" v-if="record.triggers">{{ record.triggers }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from '@/api/request';

const emotions = [
  { type: 'happy', label: '开心', icon: 'H' },
  { type: 'calm', label: '平静', icon: 'C' },
  { type: 'sad', label: '难过', icon: 'S' },
  { type: 'anxious', label: '焦虑', icon: 'A' },
  { type: 'angry', label: '生气', icon: 'G' },
  { type: 'tired', label: '疲惫', icon: 'T' },
  { type: 'confused', label: '困惑', icon: '?' },
  { type: 'lonely', label: '孤独', icon: 'L' },
];

const selectedEmotion = ref('');
const intensity = ref(5);
const triggers = ref('');
const thoughts = ref('');
const copingMethods = ref('');
const recentRecords = ref<any[]>([]);

const selectEmotion = (type: string) => {
  selectedEmotion.value = type;
};

const onIntensityChange = (e: any) => {
  intensity.value = e.detail.value;
};

const getEmotionIcon = (type: string) => {
  const emotion = emotions.find(e => e.type === type);
  return emotion?.icon || '?';
};

const formatTime = (time: string) => {
  const date = new Date(time);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return `${date.getMonth() + 1}月${date.getDate()}日`;
};

const submitRecord = async () => {
  if (!selectedEmotion.value) return;

  try {
    await api.emotionRecord.create({
      emotionType: selectedEmotion.value,
      intensity: intensity.value,
      triggers: triggers.value,
      thoughts: thoughts.value,
      copingMethods: copingMethods.value
    });

    uni.showToast({ title: '记录成功', icon: 'success' });
    selectedEmotion.value = '';
    intensity.value = 5;
    triggers.value = '';
    thoughts.value = '';
    copingMethods.value = '';
    loadRecentRecords();
  } catch (error) {
    uni.showToast({ title: '记录失败', icon: 'none' });
  }
};

const loadRecentRecords = async () => {
  try {
    const data = await api.emotionRecord.getRecent(10);
    recentRecords.value = data;
  } catch (error) {
    console.error('加载记录失败', error);
  }
};

onMounted(() => {
  loadRecentRecords();
});
</script>

<style scoped>
.emotion-page {
  padding: 20px;
  background: #f8fafc;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.emotion-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-bottom: 24px;
}

.emotion-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.emotion-item.active {
  border-color: #6366f1;
  background: #eef2ff;
}

.emotion-icon-wrapper {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.emotion-icon-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.emotion-label {
  font-size: 14px;
  color: #64748b;
}

.intensity-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 12px;
  display: block;
}

.intensity-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.form-section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
  display: block;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
}

.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  border: none;
}

.submit-btn[disabled] {
  opacity: 0.5;
}

.history-section {
  margin-top: 32px;
}

.history-list {
  margin-top: 12px;
}

.history-item {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.history-emotion-wrapper {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-emotion-text {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.history-type {
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
}

.history-intensity {
  margin-left: auto;
  font-size: 12px;
  color: #6366f1;
  background: #eef2ff;
  padding: 4px 8px;
  border-radius: 4px;
}

.history-time {
  font-size: 12px;
  color: #94a3b8;
  display: block;
  margin-bottom: 8px;
}

.history-trigger {
  font-size: 14px;
  color: #64748b;
  display: block;
}
</style>
