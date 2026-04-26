<template>
  <view class="result-page">
    <view class="result-card">
      <view class="score-section">
        <text class="score-label">测评得分</text>
        <text class="score-value">{{ record?.totalScore }}</text>
        <view class="level-badge" :class="getLevelClass(record?.resultLevel)">
          {{ getLevelName(record?.resultLevel) }}
        </view>
      </view>

      <view class="interpretation-section">
        <text class="section-title">结果解读</text>
        <text class="interpretation-text">{{ record?.resultInterpretation }}</text>
      </view>

      <view class="recommendations-section" v-if="record?.recommendations">
        <text class="section-title">建议</text>
        <text class="recommendations-text">{{ record?.recommendations }}</text>
      </view>
    </view>

    <view class="action-section">
      <button class="action-btn primary" @click="goToChat">
        与AI助手聊聊
      </button>
      <button class="action-btn secondary" @click="goBack">
        返回测评列表
      </button>
    </view>

    <view class="tips-section">
      <text class="tips-title">温馨提示</text>
      <text class="tips-text">
        测评结果仅供参考，不能作为临床诊断依据。如有需要，请咨询专业心理咨询师。
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const recordId = ref(0);
const record = ref<any>(null);

const levelNames: Record<string, string> = {
  normal: '正常',
  mild: '轻度',
  moderate: '中度',
  severe: '重度',
  unknown: '未知',
};

const levelClasses: Record<string, string> = {
  normal: 'level-green',
  mild: 'level-yellow',
  moderate: 'level-orange',
  severe: 'level-red',
  unknown: 'level-gray',
};

const getLevelName = (level: string) => levelNames[level] || level;
const getLevelClass = (level: string) => levelClasses[level] || 'level-gray';

const goToChat = () => {
  uni.switchTab({ url: '/pages/chat/index' });
};

const goBack = () => {
  uni.navigateBack();
};

const loadRecord = async () => {
  try {
    const res = await uni.request({
      url: `${import.meta.env.VITE_API_URL}/assessments/records/${recordId.value}`,
      header: {
        Authorization: `Bearer ${userStore.token}`,
      },
    });

    if (res.statusCode === 200) {
      record.value = res.data;
    }
  } catch (error) {
    console.error('加载记录失败', error);
  }
};

onMounted(() => {
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  recordId.value = Number((currentPage as any).options?.id || 0);
  
  if (recordId.value) {
    loadRecord();
  }
});
</script>

<style scoped>
.result-page {
  padding: 20px;
  background: #f8fafc;
  min-height: 100vh;
}

.result-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}

.score-section {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 24px;
}

.score-label {
  font-size: 14px;
  color: #64748b;
  display: block;
  margin-bottom: 8px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

.level-badge {
  display: inline-block;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 20px;
}

.level-green {
  background: #dcfce7;
  color: #16a34a;
}

.level-yellow {
  background: #fef9c3;
  color: #ca8a04;
}

.level-orange {
  background: #ffedd5;
  color: #ea580c;
}

.level-red {
  background: #fee2e2;
  color: #dc2626;
}

.level-gray {
  background: #f1f5f9;
  color: #64748b;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
  display: block;
}

.interpretation-section {
  margin-bottom: 24px;
}

.interpretation-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
}

.recommendations-section {
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.recommendations-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.action-btn {
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.action-btn.secondary {
  background: #f1f5f9;
  color: #64748b;
}

.tips-section {
  background: #fffbeb;
  border-radius: 12px;
  padding: 16px;
}

.tips-title {
  font-size: 14px;
  font-weight: 500;
  color: #d97706;
  margin-bottom: 8px;
  display: block;
}

.tips-text {
  font-size: 13px;
  color: #92400e;
  line-height: 1.6;
}
</style>
