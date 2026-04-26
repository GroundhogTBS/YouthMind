<template>
  <view class="emotion-picker">
    <text class="picker-title">{{ title }}</text>
    <view class="emotion-grid">
      <view
        v-for="emotion in emotions"
        :key="emotion.type"
        class="emotion-item"
        :class="{ selected: modelValue === emotion.type }"
        @click="handleSelect(emotion.type)"
      >
        <text class="emotion-icon">{{ emotion.icon }}</text>
        <text class="emotion-label">{{ emotion.label }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string;
  title?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const emotions = [
  { type: 'happy', label: '开心', icon: '😊' },
  { type: 'calm', label: '平静', icon: '😌' },
  { type: 'sad', label: '难过', icon: '😢' },
  { type: 'anxious', label: '焦虑', icon: '😰' },
  { type: 'angry', label: '生气', icon: '😠' },
  { type: 'tired', label: '疲惫', icon: '😴' },
  { type: 'confused', label: '困惑', icon: '🤔' },
  { type: 'lonely', label: '孤独', icon: '😔' },
];

const handleSelect = (type: string) => {
  emit('update:modelValue', type);
};
</script>

<style scoped>
.emotion-picker {
  background: white;
  border-radius: 16px;
  padding: 20px;
}

.picker-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  text-align: center;
  margin-bottom: 20px;
  display: block;
}

.emotion-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.emotion-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}

.emotion-item:hover {
  background: #f1f5f9;
}

.emotion-item.selected {
  border-color: #6366f1;
  background: #eef2ff;
}

.emotion-icon {
  font-size: 32px;
  margin-bottom: 4px;
}

.emotion-label {
  font-size: 14px;
  color: #64748b;
}

.emotion-item.selected .emotion-label {
  color: #6366f1;
  font-weight: 500;
}
</style>
