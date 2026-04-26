<template>
  <div class="content-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>内容管理</span>
          <el-button type="primary" @click="showCreateDialog">新增文章</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="文章" name="articles">
          <el-table :data="articleList" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="viewCount" label="浏览量" width="100" />
            <el-table-column prop="isPublished" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.isPublished ? 'success' : 'info'">
                  {{ row.isPublished ? '已发布' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="publishedAt" label="发布时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link>编辑</el-button>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="音频资源" name="audio">
          <el-table :data="audioList" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="duration" label="时长" width="100" />
            <el-table-column prop="playCount" label="播放量" width="100" />
            <el-table-column label="操作" width="150">
              <template #default>
                <el-button type="primary" link>编辑</el-button>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('articles')

const articleList = ref([
  { id: 1, title: '如何应对考试焦虑', category: '学习方法', viewCount: 1234, isPublished: true, publishedAt: '2024-01-10' },
  { id: 2, title: '和朋友吵架了怎么办', category: '人际关系', viewCount: 856, isPublished: true, publishedAt: '2024-01-08' },
  { id: 3, title: '情绪调节小技巧', category: '情绪管理', viewCount: 567, isPublished: false, publishedAt: '' },
])

const audioList = ref([
  { id: 1, title: '睡前放松冥想', category: '冥想', duration: '15:00', playCount: 2345 },
  { id: 2, title: '舒缓钢琴曲', category: '音乐', duration: '30:00', playCount: 1890 },
])

function showCreateDialog() {
  // TODO: 显示创建对话框
}
</script>

<style lang="scss" scoped>
.content-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
