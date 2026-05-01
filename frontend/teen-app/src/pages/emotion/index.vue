<template>
  <view class="emotion-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">情绪记录</text>
        <text class="header-subtitle">记录并追踪你的情绪变化</text>
      </view>
      <view class="header-right"></view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view class="tabs">
        <view class="tab-item" :class="{ active: activeTab === 'record' }" @click="activeTab = 'record'">
          <text>记录情绪</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 'trend' }" @click="activeTab = 'trend'">
          <text>情绪趋势</text>
        </view>
      </view>

      <view v-if="activeTab === 'record'" class="tab-content">
        <view class="section">
          <text class="section-title">今天心情如何？</text>
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
        </view>

        <view class="section" v-if="selectedEmotion">
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

        <view class="section" v-if="selectedEmotion">
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
      </view>

      <view v-if="activeTab === 'trend'" class="tab-content">
        <view class="section" v-if="emotionDistribution.length > 0">
          <text class="section-title">情绪分布</text>
          <view class="emotion-chart">
            <view v-for="(item, index) in emotionDistribution" :key="index" class="chart-bar-item">
              <text class="chart-label">{{ getEmotionLabel(item.emotion_type) }}</text>
              <view class="chart-bar-bg">
                <view class="chart-bar-fill" :style="{ width: getBarWidth(item.count) }"></view>
              </view>
              <text class="chart-count">{{ item.count }}</text>
            </view>
          </view>
        </view>

        <view class="section" v-if="trendData.length > 0">
          <text class="section-title">近7天记录</text>
          <view class="trend-chart">
            <view v-for="item in trendData" :key="item.date" class="trend-item">
              <text class="trend-date">{{ formatDate(item.date) }}</text>
              <view class="trend-bar-wrapper">
                <view 
                  v-for="e in item.emotions" 
                  :key="e.type" 
                  class="trend-bar"
                  :style="{ height: (e.intensity * 10) + '%', background: getEmotionColor(e.type) }"
                ></view>
              </view>
              <text class="trend-count">{{ item.count }}次</text>
            </view>
          </view>
        </view>

        <view class="section" v-if="recentRecords.length > 0">
          <text class="section-title">最近记录</text>
          <view class="history-list">
            <view 
              v-for="record in recentRecords" 
              :key="record.id" 
              class="history-item"
            >
              <view class="history-header">
                <view class="history-emotion-wrapper" :style="{ background: getEmotionColor(record.emotionType) }">
                  <text class="history-emotion-text">{{ getEmotionIcon(record.emotionType) }}</text>
                </view>
                <text class="history-type">{{ getEmotionLabel(record.emotionType) }}</text>
                <text class="history-intensity">强度: {{ record.intensity }}</text>
              </view>
              <text class="history-time">{{ formatTime(record.recordedAt) }}</text>
              <text class="history-trigger" v-if="record.triggers">{{ record.triggers }}</text>
            </view>
          </view>
        </view>

        <view class="section empty-section" v-if="emotionDistribution.length === 0 && recentRecords.length === 0">
          <text class="empty-text">暂无情绪记录</text>
          <text class="empty-hint">开始记录你的情绪吧！</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { api } from '@/api/request';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const activeTab = ref('record');

const emotions = [
  { type: 'happy', label: '开心', icon: 'H', color: '#22c55e' },
  { type: 'calm', label: '平静', icon: 'C', color: '#3b82f6' },
  { type: 'sad', label: '难过', icon: 'S', color: '#6366f1' },
  { type: 'anxious', label: '焦虑', icon: 'A', color: '#f59e0b' },
  { type: 'angry', label: '生气', icon: 'G', color: '#ef4444' },
  { type: 'tired', label: '疲惫', icon: 'T', color: '#8b5cf6' },
  { type: 'confused', label: '困惑', icon: '?', color: '#ec4899' },
  { type: 'lonely', label: '孤独', icon: 'L', color: '#64748b' },
];

const selectedEmotion = ref('');
const intensity = ref(5);
const triggers = ref('');
const thoughts = ref('');
const copingMethods = ref('');
const recentRecords = ref<any[]>([]);
const emotionDistribution = ref<any[]>([]);
const trendData = ref<any[]>([]);

const maxCount = computed(() => Math.max(...emotionDistribution.value.map(e => e.count), 1));

onMounted(() => {
  userStore.checkLogin();
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再记录情绪',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/auth/login' })
        } else {
          uni.navigateBack()
        }
      }
    });
    return;
  }
  loadRecentRecords();
  loadTrendData();
});

const selectEmotion = (type: string) => {
  selectedEmotion.value = type;
  uni.vibrateShort({ type: 'light' });
};

const onIntensityChange = (e: any) => {
  intensity.value = e.detail.value;
};

const getEmotionIcon = (type: string) => {
  const emotion = emotions.find(e => e.type === type);
  return emotion?.icon || '?';
};

const getEmotionLabel = (type: string) => {
  const emotion = emotions.find(e => e.type === type);
  return emotion?.label || type;
};

const getEmotionColor = (type: string) => {
  const emotion = emotions.find(e => e.type === type);
  return emotion?.color || '#6366f1';
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

const formatDate = (date: string) => {
  const d = new Date(date);
  return `${d.getMonth() + 1}/${d.getDate()}`;
};

const getBarWidth = (count: number) => {
  return `${Math.max((count / maxCount.value) * 100, 5)}%`;
};

const submitRecord = async () => {
  if (!selectedEmotion.value) return;
  
  if (!userStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' });
    return;
  }

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
    loadTrendData();
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

const loadTrendData = async () => {
  try {
    const data = await api.emotionRecord.getTrend(7);
    emotionDistribution.value = data.distribution || [];
    trendData.value = data.daily_trend || [];
  } catch (error) {
    console.error('加载趋势失败', error);
  }
};

function handleGoBack() {
  uni.navigateBack();
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.emotion-page {
  @extend .page-wrapper;
  flex-direction: column;
}

.page-header {
  @extend .page-header;
  background: $bg-primary;
}

.header-left, .header-right {
  width: 40px;
}

.back-btn {
  @extend .back-button;
}

.header-center {
  @include flex-column;
  align-items: center;
}

.header-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $text-primary;
}

.header-subtitle {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-top: 2px;
}

.page-content {
  flex: 1;
  height: 0;
}

.tabs {
  display: flex;
  background: $bg-primary;
  border-bottom: 1px solid $border-light;
}

.tab-item {
  flex: 1;
  padding: $spacing-md;
  text-align: center;
  font-size: $font-size-sm;
  color: $text-muted;
  
  &.active {
    color: $primary-color;
    border-bottom: 2px solid $primary-color;
  }
}

.tab-content {
  padding: $spacing-md;
}

.section {
  background: $bg-primary;
  border-radius: $radius-xl;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
}

.section-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: $spacing-md;
  display: block;
}

.emotion-selector {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  justify-content: center;
}

.emotion-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-sm $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-lg;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  
  &:active {
    transform: scale(0.95);
  }
}

.emotion-item.active {
  border-color: $primary-color;
  background: rgba($primary-color, 0.15);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba($primary-color, 0.2);
}

.emotion-icon-wrapper {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, $primary-color, rgba($primary-color, 0.8));
  border-radius: 50%;
  @include flex-center;
  margin-bottom: $spacing-xs;
}

.emotion-icon-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.emotion-label {
  font-size: $font-size-xs;
  color: $text-secondary;
}

.intensity-labels {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: $spacing-xs;
}

.form-item {
  margin-bottom: $spacing-md;
}

.form-label {
  font-size: $font-size-sm;
  font-weight: 500;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
  display: block;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  font-size: $font-size-base;
  color: $text-primary;
}

.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, $primary-color, rgba($primary-color, 0.8));
  color: white;
  border-radius: $radius-xl;
  font-size: $font-size-base;
  font-weight: 500;
  border: none;
}

.submit-btn[disabled] {
  opacity: 0.5;
}

.emotion-chart {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.chart-bar-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.chart-label {
  width: 50px;
  font-size: $font-size-sm;
  color: $text-secondary;
  text-align: right;
}

.chart-bar-bg {
  flex: 1;
  height: 20px;
  background: $bg-secondary;
  border-radius: 10px;
  overflow: hidden;
}

.chart-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary-color, rgba($primary-color, 0.6));
  border-radius: 10px;
}

.chart-count {
  width: 30px;
  font-size: $font-size-sm;
  color: $text-primary;
  font-weight: 600;
}

.trend-chart {
  display: flex;
  justify-content: space-between;
  height: 120px;
  padding-top: 20px;
}

.trend-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
}

.trend-date {
  font-size: $font-size-xs;
  color: $text-muted;
}

.trend-bar-wrapper {
  width: 20px;
  height: 80px;
  background: $bg-secondary;
  border-radius: 10px;
  display: flex;
  flex-direction: column-reverse;
  overflow: hidden;
}

.trend-bar {
  width: 100%;
  min-height: 4px;
  border-radius: 2px;
}

.trend-count {
  font-size: $font-size-xs;
  color: $text-muted;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.history-item {
  background: $bg-secondary;
  border-radius: $radius-lg;
  padding: $spacing-md;
}

.history-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-xs;
}

.history-emotion-wrapper {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  @include flex-center;
}

.history-emotion-text {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.history-type {
  font-size: $font-size-base;
  font-weight: 500;
  color: $text-primary;
}

.history-intensity {
  margin-left: auto;
  font-size: $font-size-xs;
  color: $primary-color;
  background: rgba($primary-color, 0.1);
  padding: 4px $spacing-sm;
  border-radius: $radius-sm;
}

.history-time {
  font-size: $font-size-xs;
  color: $text-muted;
  display: block;
  margin-bottom: $spacing-xs;
}

.history-trigger {
  font-size: $font-size-sm;
  color: $text-secondary;
  display: block;
}

.empty-section {
  @include flex-column;
  align-items: center;
  padding: 40px 20px;
}

.empty-text {
  font-size: $font-size-base;
  color: $text-muted;
  margin-bottom: $spacing-sm;
}

.empty-hint {
  font-size: $font-size-sm;
  color: $primary-color;
}
</style>
