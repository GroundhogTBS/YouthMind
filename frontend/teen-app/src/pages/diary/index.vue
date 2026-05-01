<template>
  <view class="diary-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">我的日记</text>
        <text class="header-subtitle">记录生活的点滴</text>
      </view>
      <view class="header-right">
        <view class="add-btn" @click="showWriteModal = true">
          <text>+</text>
        </view>
      </view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view class="tabs">
        <view class="tab-item" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
          <text>日记列表</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 'calendar' }" @click="activeTab = 'calendar'">
          <text>日历视图</text>
        </view>
      </view>

      <view v-if="activeTab === 'list'" class="tab-content">
        <view v-if="diaries.length === 0" class="empty-state">
          <text class="empty-text">还没有日记</text>
          <text class="empty-hint">点击右上角 + 开始写日记</text>
        </view>

        <view v-for="diary in diaries" :key="diary.id" class="diary-card" @click="viewDiary(diary)">
          <view class="diary-header">
            <text class="diary-date">{{ formatDate(diary.createdAt) }}</text>
            <view v-if="diary.mood" class="diary-mood" :style="{ background: getMoodColor(diary.mood) }">
              <text>{{ getMoodIcon(diary.mood) }}</text>
            </view>
          </view>
          <text class="diary-title" v-if="diary.title">{{ diary.title }}</text>
          <text class="diary-content">{{ truncate(diary.content, 100) }}</text>
          <view class="diary-footer">
            <text class="diary-weather" v-if="diary.weather">{{ getWeatherIcon(diary.weather) }} {{ diary.weather }}</text>
            <text class="diary-time">{{ formatTime(diary.createdAt) }}</text>
          </view>
        </view>
      </view>

      <view v-if="activeTab === 'calendar'" class="tab-content">
        <view class="calendar-header">
          <view class="calendar-nav" @click="prevMonth">
            <text>‹</text>
          </view>
          <text class="calendar-title">{{ currentYear }}年{{ currentMonth }}月</text>
          <view class="calendar-nav" @click="nextMonth">
            <text>›</text>
          </view>
        </view>
        <view class="calendar-weekdays">
          <text v-for="day in weekdays" :key="day" class="weekday">{{ day }}</text>
        </view>
        <view class="calendar-days">
          <view 
            v-for="(day, index) in calendarDays" 
            :key="index" 
            class="calendar-day"
            :class="{ 
              'has-diary': day.hasDiary, 
              'is-today': day.isToday,
              'is-empty': !day.date 
            }"
            @click="day.hasDiary && showDayDiaries(day.date)"
          >
            <text v-if="day.date">{{ day.date }}</text>
            <view v-if="day.hasDiary" class="diary-dot"></view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="modal-overlay" v-if="showWriteModal" @click="showWriteModal = false">
      <view class="modal-content write-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingDiary ? '编辑日记' : '写日记' }}</text>
          <view class="modal-close" @click="closeWriteModal">
            <text>×</text>
          </view>
        </view>
        <scroll-view class="modal-body" scroll-y>
          <view class="form-item">
            <text class="form-label">标题（可选）</text>
            <input class="form-input" v-model="writeForm.title" placeholder="给日记起个标题" />
          </view>
          <view class="form-item">
            <text class="form-label">今天的心情</text>
            <view class="mood-selector">
              <view 
                v-for="mood in moods" 
                :key="mood.type" 
                class="mood-item"
                :class="{ active: writeForm.mood === mood.type }"
                @click="writeForm.mood = mood.type"
              >
                <text class="mood-icon">{{ mood.icon }}</text>
                <text class="mood-label">{{ mood.label }}</text>
              </view>
            </view>
          </view>
          <view class="form-item">
            <text class="form-label">天气</text>
            <view class="weather-selector">
              <view 
                v-for="weather in weathers" 
                :key="weather.type" 
                class="weather-item"
                :class="{ active: writeForm.weather === weather.type }"
                @click="writeForm.weather = weather.type"
              >
                <text class="weather-icon">{{ weather.icon }}</text>
              </view>
            </view>
          </view>
          <view class="form-item">
            <text class="form-label">内容</text>
            <textarea 
              class="form-textarea diary-textarea" 
              v-model="writeForm.content" 
              placeholder="写下今天的故事..."
            />
          </view>
        </scroll-view>
        <view class="modal-footer">
          <view v-if="editingDiary" class="delete-btn" @click="deleteDiary">
            <text>删除</text>
          </view>
          <view class="cancel-btn" @click="closeWriteModal">
            <text>取消</text>
          </view>
          <view class="confirm-btn" @click="saveDiary">
            <text>保存</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api/request'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const activeTab = ref('list')
const diaries = ref<any[]>([])
const showWriteModal = ref(false)
const editingDiary = ref<any>(null)
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const moods = [
  { type: 'happy', label: '开心', icon: '😊' },
  { type: 'calm', label: '平静', icon: '😌' },
  { type: 'sad', label: '难过', icon: '😢' },
  { type: 'anxious', label: '焦虑', icon: '😰' },
  { type: 'angry', label: '生气', icon: '😠' },
  { type: 'tired', label: '疲惫', icon: '😴' },
]

const weathers = [
  { type: 'sunny', icon: '☀️' },
  { type: 'cloudy', icon: '☁️' },
  { type: 'rainy', icon: '🌧️' },
  { type: 'snowy', icon: '❄️' },
  { type: 'windy', icon: '💨' },
]

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const writeForm = reactive({
  title: '',
  content: '',
  mood: '',
  weather: ''
})

const calendarDays = computed(() => {
  const days: any[] = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  const today = new Date()
  
  const startPadding = firstDay.getDay()
  for (let i = 0; i < startPadding; i++) {
    days.push({ date: null, hasDiary: false, isToday: false })
  }
  
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const dateStr = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    const hasDiary = diaries.value.some(d => d.createdAt.startsWith(dateStr))
    const isToday = today.getFullYear() === currentYear.value && 
                    today.getMonth() + 1 === currentMonth.value && 
                    today.getDate() === i
    days.push({ date: i, hasDiary, isToday, dateStr })
  }
  
  return days
})

onMounted(() => {
  userStore.checkLogin()
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '提示',
      content: '请先登录后再查看日记',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/auth/login' })
        } else {
          uni.navigateBack()
        }
      }
    })
    return
  }
  loadDiaries()
})

async function loadDiaries() {
  try {
    diaries.value = await api.diary.getList(50)
  } catch (e) {
    console.error('加载日记失败', e)
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

function formatTime(dateStr: string): string {
  const d = new Date(dateStr)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function truncate(text: string, length: number): string {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

function getMoodIcon(type: string): string {
  const mood = moods.find(m => m.type === type)
  return mood?.icon || ''
}

function getMoodColor(type: string): string {
  const colors: Record<string, string> = {
    happy: '#22c55e',
    calm: '#3b82f6',
    sad: '#6366f1',
    anxious: '#f59e0b',
    angry: '#ef4444',
    tired: '#8b5cf6'
  }
  return colors[type] || '#6366f1'
}

function getWeatherIcon(type: string): string {
  const weather = weathers.find(w => w.type === type)
  return weather?.icon || ''
}

function viewDiary(diary: any) {
  editingDiary.value = diary
  writeForm.title = diary.title || ''
  writeForm.content = diary.content
  writeForm.mood = diary.mood || ''
  writeForm.weather = diary.weather || ''
  showWriteModal.value = true
}

function closeWriteModal() {
  showWriteModal.value = false
  editingDiary.value = null
  writeForm.title = ''
  writeForm.content = ''
  writeForm.mood = ''
  writeForm.weather = ''
}

async function saveDiary() {
  if (!writeForm.content.trim()) {
    uni.showToast({ title: '请输入日记内容', icon: 'none' })
    return
  }

  try {
    if (editingDiary.value) {
      await api.diary.update(editingDiary.value.id, {
        title: writeForm.title,
        content: writeForm.content,
        mood: writeForm.mood,
        weather: writeForm.weather
      })
      uni.showToast({ title: '日记已更新', icon: 'success' })
    } else {
      await api.diary.create({
        title: writeForm.title,
        content: writeForm.content,
        mood: writeForm.mood,
        weather: writeForm.weather
      })
      uni.showToast({ title: '日记已保存', icon: 'success' })
    }
    closeWriteModal()
    loadDiaries()
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

async function deleteDiary() {
  if (!editingDiary.value) return
  
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这篇日记吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await api.diary.delete(editingDiary.value.id)
          uni.showToast({ title: '日记已删除', icon: 'success' })
          closeWriteModal()
          loadDiaries()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

function showDayDiaries(dateStr: string) {
  const dayDiaries = diaries.value.filter(d => d.createdAt.startsWith(dateStr))
  if (dayDiaries.length === 1) {
    viewDiary(dayDiaries[0])
  } else if (dayDiaries.length > 1) {
    uni.showActionSheet({
      itemList: dayDiaries.map(d => d.title || truncate(d.content, 20)),
      success: (res) => {
        viewDiary(dayDiaries[res.tapIndex])
      }
    })
  }
}

function handleGoBack() {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.diary-page {
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

.add-btn {
  width: 32px;
  height: 32px;
  background: $primary-color;
  border-radius: 50%;
  @include flex-center;
  
  text {
    font-size: 20px;
    color: #fff;
    line-height: 1;
  }
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

.empty-state {
  @include flex-column;
  align-items: center;
  padding: 60px 20px;
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

.diary-card {
  background: $bg-primary;
  border-radius: $radius-xl;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
}

.diary-date {
  font-size: $font-size-sm;
  color: $primary-color;
  font-weight: 500;
}

.diary-mood {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  @include flex-center;
  
  text {
    font-size: 12px;
  }
}

.diary-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: $spacing-xs;
}

.diary-content {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
  display: block;
  margin-bottom: $spacing-sm;
}

.diary-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.diary-weather {
  font-size: $font-size-xs;
  color: $text-muted;
}

.diary-time {
  font-size: $font-size-xs;
  color: $text-light;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md;
  background: $bg-primary;
  border-radius: $radius-xl;
  margin-bottom: $spacing-md;
}

.calendar-nav {
  width: 32px;
  height: 32px;
  @include flex-center;
  
  text {
    font-size: 20px;
    color: $primary-color;
  }
}

.calendar-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-primary;
}

.calendar-weekdays {
  display: flex;
  background: $bg-primary;
  border-radius: $radius-lg $radius-lg 0 0;
  padding: $spacing-sm;
}

.weekday {
  flex: 1;
  text-align: center;
  font-size: $font-size-xs;
  color: $text-muted;
}

.calendar-days {
  display: flex;
  flex-wrap: wrap;
  background: $bg-primary;
  border-radius: 0 0 $radius-lg $radius-lg;
  padding: $spacing-sm;
}

.calendar-day {
  width: calc(100% / 7);
  height: 40px;
  @include flex-column;
  align-items: center;
  justify-content: center;
  position: relative;
  
  text {
    font-size: $font-size-sm;
    color: $text-primary;
  }
  
  &.is-empty {
    text {
      color: transparent;
    }
  }
  
  &.is-today {
    background: rgba($primary-color, 0.1);
    border-radius: 50%;
    
    text {
      color: $primary-color;
      font-weight: 600;
    }
  }
  
  &.has-diary {
    .diary-dot {
      position: absolute;
      bottom: 4px;
      width: 4px;
      height: 4px;
      background: $primary-color;
      border-radius: 50%;
    }
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  @include flex-center;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  background: $bg-primary;
  border-radius: $radius-xl;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-light;
}

.modal-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $text-primary;
}

.modal-close {
  width: 32px;
  height: 32px;
  @include flex-center;
  
  text {
    font-size: 24px;
    color: $text-muted;
  }
}

.modal-body {
  flex: 1;
  padding: $spacing-lg;
  overflow-y: auto;
}

.form-item {
  margin-bottom: $spacing-lg;
}

.form-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-bottom: $spacing-sm;
  display: block;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  font-size: $font-size-base;
  color: $text-primary;
}

.form-textarea {
  width: 100%;
  min-height: 120px;
  padding: $spacing-md;
  background: $bg-secondary;
  border-radius: $radius-md;
  font-size: $font-size-base;
  color: $text-primary;
}

.diary-textarea {
  min-height: 200px;
}

.mood-selector {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.mood-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-sm;
  background: $bg-secondary;
  border-radius: $radius-md;
  border: 2px solid transparent;
  
  &.active {
    border-color: $primary-color;
    background: rgba($primary-color, 0.1);
  }
}

.mood-icon {
  font-size: 20px;
  margin-bottom: 2px;
}

.mood-label {
  font-size: $font-size-xs;
  color: $text-secondary;
}

.weather-selector {
  display: flex;
  gap: $spacing-sm;
}

.weather-item {
  width: 44px;
  height: 44px;
  background: $bg-secondary;
  border-radius: $radius-md;
  @include flex-center;
  border: 2px solid transparent;
  
  &.active {
    border-color: $primary-color;
    background: rgba($primary-color, 0.1);
  }
}

.weather-icon {
  font-size: 20px;
}

.modal-footer {
  display: flex;
  padding: $spacing-lg;
  gap: $spacing-sm;
  border-top: 1px solid $border-light;
}

.delete-btn, .cancel-btn, .confirm-btn {
  flex: 1;
  height: 44px;
  border-radius: $radius-md;
  @include flex-center;
}

.delete-btn {
  background: rgba($error-color, 0.1);
  
  text {
    color: $error-color;
  }
}

.cancel-btn {
  background: $bg-secondary;
  
  text {
    color: $text-secondary;
  }
}

.confirm-btn {
  background: $primary-color;
  
  text {
    color: #fff;
  }
}
</style>
