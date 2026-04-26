<template>
  <view class="assessment-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">心理测评</text>
      </view>
      <view class="header-right"></view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view v-if="!currentScale" class="scale-list">
        <view class="section-title">选择测评量表</view>
        <view 
          v-for="scale in scales" 
          :key="scale.type" 
          class="scale-card"
          @click="startAssessment(scale.type)"
        >
          <view class="scale-icon-wrapper">
            <text class="scale-icon-text">{{ scale.name.charAt(0) }}</text>
          </view>
          <view class="scale-info">
            <text class="scale-name">{{ scale.name }}</text>
            <text class="scale-desc">{{ scale.description }}</text>
            <view class="scale-meta">
              <text class="meta-item">{{ scale.questionCount }}题</text>
              <text class="meta-item">{{ scale.estimatedTime }}</text>
            </view>
          </view>
          <text class="scale-arrow">›</text>
        </view>
      </view>

      <view v-else-if="!result" class="question-section">
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
        <text class="progress-text">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</text>
        
        <view class="question-card">
          <text class="question-text">{{ currentQuestion?.text }}</text>
        </view>

        <view class="options-list">
          <view 
            v-for="(option, index) in currentQuestion?.options" 
            :key="index"
            class="option-item"
            :class="{ selected: answers[currentQuestionIndex] === index }"
            @click="selectAnswer(index)"
          >
            <view class="option-radio">
              <view v-if="answers[currentQuestionIndex] === index" class="option-radio-inner"></view>
            </view>
            <text class="option-text">{{ option }}</text>
          </view>
        </view>

        <view class="action-buttons">
          <view 
            v-if="currentQuestionIndex > 0" 
            class="btn btn-secondary" 
            @click="prevQuestion"
          >
            上一题
          </view>
          <view 
            v-if="answers[currentQuestionIndex] !== undefined"
            class="btn btn-primary" 
            @click="nextQuestion"
          >
            {{ currentQuestionIndex === questions.length - 1 ? '提交' : '下一题' }}
          </view>
        </view>
      </view>

      <view v-else class="result-section">
        <view class="result-card">
          <view class="result-icon-wrapper">
            <text class="result-icon-text">{{ getResultIcon() }}</text>
          </view>
          <text class="result-title">{{ currentScale?.name }}</text>
          <view class="result-score">
            <text class="score-value">{{ result.totalScore }}</text>
            <text class="score-label">总分</text>
          </view>
          <view class="result-level" :class="'level-' + result.resultLevel">
            {{ result.resultLevel }}
          </view>
          <text class="result-desc">{{ result.resultDescription }}</text>
        </view>

        <view class="result-actions">
          <view class="btn btn-primary" @click="resetAssessment">
            重新测评
          </view>
          <view class="btn btn-secondary" @click="goToHistory">
            查看历史
          </view>
        </view>

        <view v-if="history.length > 0" class="history-section">
          <text class="section-title">测评历史</text>
          <view v-for="item in history" :key="item.id" class="history-item">
            <view class="history-info">
              <text class="history-name">{{ item.scaleName }}</text>
              <text class="history-time">{{ formatTime(item.createdAt) }}</text>
            </view>
            <view class="history-score">
              <text class="score-num">{{ item.totalScore }}</text>
              <text class="score-level">{{ item.resultLevel }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'
import { api } from '@/api/request'

const navStore = useNavStore()
const userStore = useUserStore()

interface Scale {
  type: string
  name: string
  description: string
  questionCount: number
  estimatedTime: string
}

interface Question {
  id: number
  text: string
  options: string[]
}

const scales = ref<Scale[]>([])
const currentScale = ref<Scale | null>(null)
const questions = ref<Question[]>([])
const currentQuestionIndex = ref(0)
const answers = ref<number[]>([])
const result = ref<any>(null)
const history = ref<any[]>([])

const progressPercent = computed(() => {
  if (questions.value.length === 0) return 0
  return ((currentQuestionIndex.value + 1) / questions.value.length) * 100
})

const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value]
})

onMounted(() => {
  userStore.checkLogin()
  loadScales()
  if (userStore.isLoggedIn) {
    loadHistory()
  }
})

async function loadScales() {
  try {
    const data = await api.assessment.getScales()
    scales.value = data
  } catch (e) {
    console.error('加载量表失败', e)
  }
}

async function loadHistory() {
  try {
    const data = await api.assessment.getHistory(5)
    history.value = data
  } catch (e) {
    console.error('加载历史失败', e)
  }
}

async function startAssessment(scaleType: string) {
  try {
    const scale = scales.value.find(s => s.type === scaleType)
    if (!scale) return
    
    currentScale.value = scale
    
    const data = await api.assessment.getScale(scaleType)
    questions.value = data.questions
    answers.value = new Array(data.questions.length).fill(undefined)
    currentQuestionIndex.value = 0
    result.value = null
  } catch (e) {
    console.error('加载量表失败', e)
  }
}

function selectAnswer(index: number) {
  answers.value[currentQuestionIndex.value] = index
}

function prevQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

async function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  } else {
    await submitAssessment()
  }
}

async function submitAssessment() {
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再提交测评',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/auth/login' })
        }
      }
    })
    return
  }
  
  try {
    const data = await api.assessment.submit(
      currentScale.value!.type,
      answers.value
    )
    result.value = data
    loadHistory()
  } catch (e) {
    console.error('提交失败', e)
    uni.showToast({ title: '提交失败', icon: 'none' })
  }
}

function resetAssessment() {
  currentScale.value = null
  questions.value = []
  answers.value = []
  currentQuestionIndex.value = 0
  result.value = null
}

function goToHistory() {
  resetAssessment()
}

function getResultIcon(): string {
  if (!result.value) return '?'
  const level = result.value.resultLevel
  if (level.includes('正常') || level.includes('满意')) return 'G'
  if (level.includes('轻度') || level.includes('一般')) return 'Y'
  return 'R'
}

function formatTime(time: string): string {
  const date = new Date(time)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function handleGoBack() {
  if (currentScale.value && !result.value) {
    uni.showModal({
      title: '提示',
      content: '确定要退出测评吗？当前进度将不会保存',
      success: (res) => {
        if (res.confirm) {
          resetAssessment()
        }
      }
    })
  } else if (result.value) {
    resetAssessment()
  } else {
    navStore.resetToHome()
    uni.navigateBack()
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.assessment-page {
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

.page-content {
  flex: 1;
  height: 0;
}

.scale-list {
  padding: $spacing-lg;
}

.section-title {
  font-size: $font-size-base;
  font-weight: 500;
  color: $text-muted;
  margin-bottom: $spacing-md;
  display: block;
}

.scale-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-xl;
  margin-bottom: $spacing-md;
}

.scale-icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: $radius-lg;
  @include flex-center;
  margin-right: $spacing-md;
  flex-shrink: 0;
}

.scale-icon-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.scale-info {
  flex: 1;
}

.scale-name {
  font-size: $font-size-base;
  font-weight: 500;
  color: $text-primary;
  display: block;
  margin-bottom: $spacing-xs;
}

.scale-desc {
  font-size: $font-size-sm;
  color: $text-muted;
  display: block;
  margin-bottom: $spacing-xs;
}

.scale-meta {
  display: flex;
  gap: $spacing-md;
}

.meta-item {
  font-size: $font-size-xs;
  color: $text-light;
}

.scale-arrow {
  font-size: $font-size-xl;
  color: $text-light;
}

.progress-bar {
  height: 4px;
  background: $bg-secondary;
  border-radius: 2px;
  margin: $spacing-lg;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary-color, rgba($primary-color, 0.8));
  transition: width 0.3s;
}

.progress-text {
  font-size: $font-size-sm;
  color: $text-muted;
  text-align: center;
  display: block;
  margin-bottom: $spacing-lg;
}

.question-card {
  margin: 0 $spacing-lg $spacing-lg;
  padding: $spacing-xl;
  background: $bg-primary;
  border-radius: $radius-xl;
}

.question-text {
  font-size: $font-size-lg;
  font-weight: 500;
  color: $text-primary;
  line-height: 1.6;
}

.options-list {
  margin: 0 $spacing-lg;
}

.option-item {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-lg;
  margin-bottom: $spacing-md;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.option-item.selected {
  border-color: $primary-color;
  background: rgba($primary-color, 0.05);
}

.option-radio {
  width: 20px;
  height: 20px;
  border: 2px solid $border-color;
  border-radius: 50%;
  margin-right: $spacing-md;
  @include flex-center;
}

.option-item.selected .option-radio {
  border-color: $primary-color;
}

.option-radio-inner {
  width: 10px;
  height: 10px;
  background: $primary-color;
  border-radius: 50%;
}

.option-text {
  font-size: $font-size-base;
  color: $text-primary;
}

.action-buttons {
  display: flex;
  gap: $spacing-md;
  margin: $spacing-xl $spacing-lg;
}

.btn {
  flex: 1;
  height: 48px;
  border-radius: $radius-xl;
  @include flex-center;
  font-size: $font-size-base;
  font-weight: 500;
}

.btn-primary {
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  color: #fff;
}

.btn-secondary {
  background: $bg-secondary;
  color: $text-primary;
}

.result-section {
  padding: $spacing-lg;
}

.result-card {
  padding: $spacing-xl;
  background: $bg-primary;
  border-radius: $radius-xl;
  text-align: center;
  margin-bottom: $spacing-lg;
}

.result-icon-wrapper {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: 50%;
  @include flex-center;
  margin: 0 auto $spacing-md;
}

.result-icon-text {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
}

.result-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: $spacing-lg;
}

.result-score {
  margin-bottom: $spacing-md;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: $primary-color;
}

.score-label {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-left: $spacing-xs;
}

.result-level {
  display: inline-block;
  padding: $spacing-xs $spacing-md;
  border-radius: $radius-md;
  font-size: $font-size-sm;
  font-weight: 500;
  margin-bottom: $spacing-md;
  
  &.level-正常, &.level-低压力, &.level-非常满意 {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.level-轻度, &.level-中等压力, &.level-一般满意 {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.level-中度, &.level-高压力, &.level-不满意 {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.level-中重度, &.level-重度, &.level-非常不满意 {
    background: rgba($danger-color, 0.2);
    color: $danger-color;
  }
}

.result-desc {
  font-size: $font-size-sm;
  color: $text-muted;
  line-height: 1.6;
}

.result-actions {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}

.history-section {
  margin-top: $spacing-lg;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg;
  background: $bg-primary;
  border-radius: $radius-lg;
  margin-bottom: $spacing-md;
}

.history-info {
  flex: 1;
}

.history-name {
  font-size: $font-size-base;
  color: $text-primary;
  display: block;
  margin-bottom: $spacing-xs;
}

.history-time {
  font-size: $font-size-xs;
  color: $text-light;
}

.history-score {
  text-align: right;
}

.score-num {
  font-size: $font-size-xl;
  font-weight: 600;
  color: $primary-color;
  display: block;
}

.score-level {
  font-size: $font-size-xs;
  color: $text-muted;
}
</style>
