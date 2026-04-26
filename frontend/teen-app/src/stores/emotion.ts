import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useEmotionStore = defineStore('emotion', () => {
  const records = ref<any[]>([]);
  const currentEmotion = ref<string>('');
  const intensity = ref<number>(5);
  const loading = ref(false);
  const statistics = ref<any>(null);

  const recentEmotions = computed(() => records.value.slice(0, 7));
  const emotionTypes = [
    { type: 'happy', label: '开心', icon: '😊' },
    { type: 'calm', label: '平静', icon: '😌' },
    { type: 'sad', label: '难过', icon: '😢' },
    { type: 'anxious', label: '焦虑', icon: '😰' },
    { type: 'angry', label: '生气', icon: '😠' },
    { type: 'tired', label: '疲惫', icon: '😴' },
    { type: 'confused', label: '困惑', icon: '🤔' },
    { type: 'lonely', label: '孤独', icon: '😔' },
  ];

  async function fetchRecords(limit: number = 20) {
    loading.value = true;
    try {
      const res = await uni.request({
        url: `${import.meta.env.VITE_API_URL}/emotions`,
        header: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (res.statusCode === 200) {
        records.value = res.data.list || [];
      }
    } catch (error) {
      console.error('Failed to fetch emotion records:', error);
    } finally {
      loading.value = false;
    }
  }

  async function createRecord(data: any) {
    loading.value = true;
    try {
      const res = await uni.request({
        url: `${import.meta.env.VITE_API_URL}/emotions`,
        method: 'POST',
        header: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        data: {
          emotionType: currentEmotion.value,
          intensity: intensity.value,
          ...data,
        },
      });
      if (res.statusCode === 201) {
        records.value.unshift(res.data);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to create emotion record:', error);
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStatistics(days: number = 30) {
    try {
      const res = await uni.request({
        url: `${import.meta.env.VITE_API_URL}/emotions/statistics?days=${days}`,
        header: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (res.statusCode === 200) {
        statistics.value = res.data;
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  }

  function setCurrentEmotion(emotion: string) {
    currentEmotion.value = emotion;
  }

  function setIntensity(value: number) {
    intensity.value = value;
  }

  return {
    records,
    currentEmotion,
    intensity,
    loading,
    statistics,
    recentEmotions,
    emotionTypes,
    fetchRecords,
    createRecord,
    fetchStatistics,
    setCurrentEmotion,
    setIntensity,
  };
});
