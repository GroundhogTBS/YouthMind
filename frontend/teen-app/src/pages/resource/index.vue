<template>
  <view class="resource-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">学习资源</text>
        <text class="header-subtitle">发现更多成长指南</text>
      </view>
      <view class="header-right"></view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false">
      <view class="category-tabs">
        <view 
          v-for="(cat, index) in categories" 
          :key="index"
          class="category-tab"
          :class="{ active: activeCategory === index }"
          @click="activeCategory = index"
        >
          <text>{{ cat.name }}</text>
        </view>
      </view>

      <view class="resource-list">
        <view 
          v-for="(item, index) in filteredResources" 
          :key="index"
          class="resource-item"
          @click="handleOpenResource(item)"
        >
          <view class="resource-icon-wrapper">
            <text class="resource-icon">{{ item.icon }}</text>
          </view>
          <view class="resource-info">
            <text class="resource-title">{{ item.title }}</text>
            <text class="resource-desc">{{ item.description }}</text>
            <view class="resource-meta">
              <text class="resource-category">{{ item.categoryName }}</text>
              <text class="resource-views">{{ item.views }}人已学习</text>
            </view>
          </view>
          <text class="resource-arrow">›</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useNavStore } from '@/stores/nav'

const navStore = useNavStore()

const activeCategory = ref(0)

const categories = [
  { name: '全部', id: 'all' },
  { name: '情绪管理', id: 'emotion' },
  { name: '学习压力', id: 'study' },
  { name: '人际关系', id: 'social' },
  { name: '自我成长', id: 'growth' }
]

const resources = ref([
  { icon: 'S', title: '如何应对考试焦虑', description: '考试前的紧张是正常的，学会这些方法让你更从容', category: 'study', categoryName: '学习压力', views: 1234 },
  { icon: 'R', title: '和朋友吵架了怎么办', description: '友谊中的冲突可以这样化解，让关系更牢固', category: 'social', categoryName: '人际关系', views: 892 },
  { icon: 'G', title: '提升自信心的10个方法', description: '相信自己，你比想象中更优秀', category: 'growth', categoryName: '自我成长', views: 1567 },
  { icon: 'E', title: '学会放松：深呼吸练习', description: '简单的呼吸技巧，帮你缓解紧张情绪', category: 'emotion', categoryName: '情绪管理', views: 2341 },
  { icon: 'Z', title: '如何改善睡眠质量', description: '好的睡眠是心理健康的基础', category: 'emotion', categoryName: '情绪管理', views: 1876 },
  { icon: 'C', title: '如何与父母有效沟通', description: '学会表达自己的想法，建立更好的亲子关系', category: 'social', categoryName: '人际关系', views: 1456 },
  { icon: 'T', title: '时间管理小技巧', description: '合理安排时间，让学习和生活更轻松', category: 'study', categoryName: '学习压力', views: 987 },
  { icon: 'M', title: '正念冥想入门指南', description: '每天10分钟，让心灵更平静', category: 'emotion', categoryName: '情绪管理', views: 2134 },
  { icon: 'K', title: '认识自己的情绪', description: '了解情绪，才能更好地管理情绪', category: 'emotion', categoryName: '情绪管理', views: 1678 },
  { icon: 'A', title: '设定目标的小技巧', description: '学会设定可实现的目标，让成长更有方向', category: 'growth', categoryName: '自我成长', views: 1123 }
])

const filteredResources = computed(() => {
  if (activeCategory.value === 0) return resources.value
  const categoryId = categories[activeCategory.value].id
  return resources.value.filter(r => r.category === categoryId)
})

function handleGoBack() {
  navStore.resetToHome()
  uni.navigateBack()
}

function handleOpenResource(item: any) {
  uni.showToast({ title: '资源详情开发中', icon: 'none' })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.resource-page {
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

.category-tabs {
  display: flex;
  padding: $spacing-md $spacing-lg;
  gap: $spacing-md;
  overflow-x: auto;
  white-space: nowrap;
  background: $bg-primary;
  border-bottom: 1px solid $border-light;
}

.category-tab {
  padding: $spacing-sm $spacing-lg;
  background: $bg-secondary;
  border-radius: $radius-full;
  font-size: $font-size-sm;
  color: $text-secondary;
  flex-shrink: 0;
  
  &.active {
    background: $primary-color;
    color: #fff;
    font-weight: 500;
  }
}

.resource-list {
  padding: $spacing-lg;
}

.resource-item {
  @include card-base;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  display: flex;
  align-items: center;
}

.resource-icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, $primary-color 0%, rgba($primary-color, 0.8) 100%);
  border-radius: $radius-lg;
  @include flex-center;
  margin-right: $spacing-lg;
  flex-shrink: 0;
}

.resource-icon {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.resource-info {
  flex: 1;
}

.resource-title {
  font-size: $font-size-base;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: $spacing-xs;
}

.resource-desc {
  font-size: $font-size-sm;
  color: $text-muted;
  display: block;
  margin-bottom: $spacing-sm;
  line-height: 1.4;
}

.resource-meta {
  display: flex;
  gap: $spacing-md;
}

.resource-category {
  font-size: $font-size-xs;
  color: $primary-color;
  background: rgba($primary-color, 0.1);
  padding: 2px $spacing-sm;
  border-radius: $radius-sm;
}

.resource-views {
  font-size: $font-size-xs;
  color: $text-muted;
}

.resource-arrow {
  font-size: $font-size-lg;
  color: $text-light;
  margin-left: $spacing-sm;
}
</style>
