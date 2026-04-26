<template>
  <view class="detail-page">
    <view class="progress-bar">
      <view class="progress" :style="{ width: progressWidth }"></view>
    </view>
    <text class="progress-text">{{ currentIndex + 1 }} / {{ questions.length }}</text>

    <view class="question-section" v-if="currentQuestion">
      <text class="question-text">{{ currentQuestion.questionText }}</text>
      
      <view class="options-list">
        <view 
          v-for="(option, index) in currentQuestion.options" 
          :key="index"
          class="option-item"
          :class="{ selected: answers[currentQuestion.questionNumber] === index }"
          @click="selectAnswer(index)"
        >
          <view class="option-radio">
            <view class="radio-inner" v-if="answers[currentQuestion.questionNumber] === index"></view>
          </view>
          <text class="option-text">{{ option }}</text>
        </view>
      </view>
    </view>

    <view class="nav-buttons">
      <button 
        class="nav-btn prev" 
        @click="prevQuestion"
        :disabled="currentIndex === 0"
      >
        上一题
      </button>
      <button 
        class="nav-btn next" 
        @click="nextQuestion"
        v-if="currentIndex < questions.length - 1"
        :disabled="answers[currentQuestion.questionNumber] === undefined"
      >
        下一题
      </button>
      <button 
        class="nav-btn submit" 
        @click="submitAssessment"
        v-else
        :disabled="!allAnswered"
      >
        提交测评
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const assessmentId = ref(0);
const assessment = ref<any>(null);
const questions = ref<any[]>([]);
const currentIndex = ref(0);
const answers = ref<Record<number, number>>({});

const currentQuestion = computed(() => questions.value[currentIndex.value]);

const progressWidth = computed(() => {
  if (questions.value.length === 0) return '0%';
  return `${((currentIndex.value + 1) / questions.value.length) * 100}%`;
});

const allAnswered = computed(() => {
  return questions.value.every(q => answers.value[q.questionNumber] !== undefined);
});

const selectAnswer = (index: number) => {
  if (currentQuestion.value) {
    answers.value[currentQuestion.value.questionNumber] = index;
  }
};

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++;
  }
};

const submitAssessment = async () => {
  const answerList = questions.value.map(q => ({
    questionNumber: q.questionNumber,
    score: q.scoring?.[answers.value[q.questionNumber]] || answers.value[q.questionNumber],
    answerText: q.options?.[answers.value[q.questionNumber]],
  }));

  try {
    uni.showLoading({ title: '提交中...' });
    
    const res = await uni.request({
      url: `${import.meta.env.VITE_API_URL}/assessments/submit`,
      method: 'POST',
      header: {
        Authorization: `Bearer ${userStore.token}`,
      },
      data: {
        assessmentId: assessmentId.value,
        answers: answerList,
      },
    });

    uni.hideLoading();

    if (res.statusCode === 201) {
      uni.redirectTo({
        url: `/pages/assessment/result?id=${res.data.id}`,
      });
    }
  } catch (error) {
    uni.hideLoading();
    uni.showToast({ title: '提交失败', icon: 'none' });
  }
};

const loadAssessment = async () => {
  try {
    const res = await uni.request({
      url: `${import.meta.env.VITE_API_URL}/assessments/${assessmentId.value}`,
      header: {
        Authorization: `Bearer ${userStore.token}`,
      },
    });

    if (res.statusCode === 200) {
      assessment.value = res.data;
      questions.value = res.data.questions || [];
    }
  } catch (error) {
    console.error('加载测评失败', error);
  }
};

onMounted(() => {
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  assessmentId.value = Number((currentPage as any).options?.id || 0);
  
  if (assessmentId.value) {
    loadAssessment();
  }
});
</script>

<style scoped>
.detail-page {
  padding: 20px;
  background: #f8fafc;
  min-height: 100vh;
}

.progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin-bottom: 8px;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  display: block;
  margin-bottom: 24px;
}

.question-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.question-text {
  font-size: 18px;
  font-weight: 500;
  color: #1e293b;
  line-height: 1.6;
  margin-bottom: 24px;
  display: block;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.option-item.selected {
  background: #eef2ff;
  border-color: #6366f1;
}

.option-radio {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-item.selected .option-radio {
  border-color: #6366f1;
}

.radio-inner {
  width: 10px;
  height: 10px;
  background: #6366f1;
  border-radius: 50%;
}

.option-text {
  font-size: 15px;
  color: #334155;
}

.nav-buttons {
  display: flex;
  gap: 12px;
}

.nav-btn {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  border: none;
}

.nav-btn.prev {
  background: #f1f5f9;
  color: #64748b;
}

.nav-btn.next {
  background: #6366f1;
  color: white;
}

.nav-btn.submit {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.nav-btn[disabled] {
  opacity: 0.5;
}
</style>
