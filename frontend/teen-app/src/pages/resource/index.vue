<template>
  <view class="resource-page">
    <view class="page-header">
      <view class="header-left">
        <view class="back-btn" @click="handleGoBack">
          <text>←</text>
        </view>
      </view>
      <view class="header-center">
        <text class="header-title">{{ isFavorites ? '我的收藏' : '学习资源' }}</text>
        <text class="header-subtitle">{{ isFavorites ? '收藏的文章' : '发现更多成长指南' }}</text>
      </view>
      <view class="header-right"></view>
    </view>

    <scroll-view class="page-content" scroll-y :show-scrollbar="false" @scrolltolower="loadMore">
      <view class="category-tabs" v-if="!isFavorites">
        <view 
          v-for="(cat, index) in categories" 
          :key="cat.key"
          class="category-tab"
          :class="{ active: activeCategory === index }"
          @click="selectCategory(index)"
        >
          <text>{{ cat.name }}</text>
        </view>
      </view>

      <view class="resource-list">
        <view v-if="loading && articles.length === 0" class="loading-state">
          <text>加载中...</text>
        </view>
        
        <view v-else-if="articles.length === 0" class="empty-state">
          <text class="empty-text">{{ isFavorites ? '暂无收藏' : '暂无文章' }}</text>
        </view>

        <view 
          v-for="article in articles" 
          :key="article.id"
          class="resource-item"
          @click="openArticle(article)"
        >
          <view class="resource-icon-wrapper">
            <text class="resource-icon">{{ getCategoryIcon(article.category) }}</text>
          </view>
          <view class="resource-info">
            <text class="resource-title">{{ article.title }}</text>
            <text class="resource-desc">{{ article.summary }}</text>
            <view class="resource-meta">
              <text class="resource-category">{{ getCategoryName(article.category) }}</text>
              <text class="resource-views">{{ article.viewCount }}人已学习</text>
            </view>
          </view>
          <text class="resource-arrow">›</text>
        </view>
      </view>
    </scroll-view>

    <view class="article-modal" v-if="showArticleModal" @click="closeArticle">
      <view class="article-content" @click.stop>
        <view class="article-header">
          <view class="article-close" @click="closeArticle">
            <text>×</text>
          </view>
          <text class="article-category-tag">{{ getCategoryName(currentArticle?.category || '') }}</text>
          <text class="article-title-lg">{{ currentArticle?.title }}</text>
        </view>
        <scroll-view class="article-body" scroll-y>
          <rich-text :nodes="formatContent(currentArticle?.content || '')"></rich-text>
        </scroll-view>
        <view class="article-footer">
          <view class="action-btn" :class="{ favorited: currentArticle?.isFavorited }" @click="toggleFavorite">
            <text>{{ currentArticle?.isFavorited ? '已收藏' : '收藏' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useNavStore } from '@/stores/nav'
import { useUserStore } from '@/stores/user'
import { api } from '@/api/request'

const navStore = useNavStore()
const userStore = useUserStore()

const isFavorites = ref(false)
const activeCategory = ref(0)
const articles = ref<any[]>([])
const loading = ref(false)
const showArticleModal = ref(false)
const currentArticle = ref<any>(null)

const categories = ref([
  { key: 'all', name: '全部' },
  { key: 'emotion', name: '情绪管理' },
  { key: 'stress', name: '压力调节' },
  { key: 'relationship', name: '人际关系' },
  { key: 'study', name: '学习心理' },
  { key: 'growth', name: '自我成长' }
])

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  if (currentPage?.options?.tab === 'favorites') {
    isFavorites.value = true
  }
  
  loadArticles()
})

async function loadArticles() {
  if (loading.value) return
  loading.value = true
  
  try {
    let data
    if (isFavorites.value) {
      data = await api.article.getFavorites()
    } else {
      const category = activeCategory.value === 0 ? undefined : categories.value[activeCategory.value].key
      data = await api.article.getList(category)
    }
    articles.value = data
  } catch (e) {
    console.error('加载文章失败', e)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
}

function selectCategory(index: number) {
  activeCategory.value = index
  loadArticles()
}

async function openArticle(article: any) {
  try {
    const data = await api.article.getById(article.id)
    currentArticle.value = data
    showArticleModal.value = true
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

function closeArticle() {
  showArticleModal.value = false
  currentArticle.value = null
}

async function toggleFavorite() {
  if (!currentArticle.value) return
  
  try {
    if (currentArticle.value.isFavorited) {
      await api.article.unfavorite(currentArticle.value.id)
      currentArticle.value.isFavorited = false
      uni.showToast({ title: '已取消收藏', icon: 'success' })
    } else {
      await api.article.favorite(currentArticle.value.id)
      currentArticle.value.isFavorited = true
      uni.showToast({ title: '收藏成功', icon: 'success' })
    }
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function getCategoryName(key: string): string {
  const cat = categories.value.find(c => c.key === key)
  return cat?.name || key
}

function getCategoryIcon(key: string): string {
  const icons: Record<string, string> = {
    emotion: 'E',
    stress: 'S',
    relationship: 'R',
    study: 'T',
    growth: 'G'
  }
  return icons[key] || 'A'
}

function formatContent(content: string): string {
  return content
    .replace(/\n/g, '<br/>')
    .replace(/##\s*(.+)/g, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\d+\.\s+/g, '<br/><strong>$&</strong>')
}

function handleGoBack() {
  navStore.resetToHome()
  uni.navigateBack()
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

.loading-state, .empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-text {
  font-size: $font-size-base;
  color: $text-muted;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.article-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  @include flex-center;
}

.article-content {
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  background: $bg-primary;
  border-radius: $radius-xl;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.article-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-light;
  position: relative;
}

.article-close {
  position: absolute;
  top: $spacing-md;
  right: $spacing-md;
  width: 32px;
  height: 32px;
  @include flex-center;
  
  text {
    font-size: 24px;
    color: $text-muted;
  }
}

.article-category-tag {
  font-size: $font-size-xs;
  color: $primary-color;
  background: rgba($primary-color, 0.1);
  padding: 4px $spacing-md;
  border-radius: $radius-sm;
  display: inline-block;
  margin-bottom: $spacing-sm;
}

.article-title-lg {
  font-size: $font-size-xl;
  font-weight: 600;
  color: $text-primary;
  display: block;
  padding-right: 40px;
}

.article-body {
  flex: 1;
  padding: $spacing-lg;
  font-size: $font-size-base;
  color: $text-primary;
  line-height: 1.8;
  
  h3 {
    font-size: $font-size-lg;
    font-weight: 600;
    margin: $spacing-lg 0 $spacing-md;
    color: $text-primary;
  }
  
  strong {
    font-weight: 600;
    color: $text-primary;
  }
}

.article-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-light;
  display: flex;
  justify-content: center;
}

.action-btn {
  padding: $spacing-md $spacing-2xl;
  background: $bg-secondary;
  border-radius: $radius-full;
  
  text {
    font-size: $font-size-base;
    color: $text-secondary;
  }
  
  &.favorited {
    background: rgba($primary-color, 0.1);
    
    text {
      color: $primary-color;
    }
  }
}
</style>
