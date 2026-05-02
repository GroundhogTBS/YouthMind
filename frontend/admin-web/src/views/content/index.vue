<template>
  <div class="content-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>内容管理</span>
          <el-button type="primary" @click="showCreateDialog">新增文章</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="文章" name="articles">
          <el-table :data="articleList" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                {{ getCategoryName(row.category) }}
              </template>
            </el-table-column>
            <el-table-column prop="viewCount" label="浏览量" width="100" />
            <el-table-column prop="isPublished" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.isPublished ? 'success' : 'info'">
                  {{ row.isPublished ? '已发布' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link @click="editArticle(row)">编辑</el-button>
                <el-button type="danger" link @click="deleteArticle(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="音频资源" name="audio">
          <el-empty description="音频资源功能开发中..." />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑文章' : '新增文章'" width="700px">
      <el-form :model="articleForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="articleForm.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="articleForm.category" placeholder="请选择分类">
            <el-option v-for="cat in categories" :key="cat.key" :label="cat.name" :value="cat.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="articleForm.summary" type="textarea" :rows="2" placeholder="请输入文章摘要" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="articleForm.content" type="textarea" :rows="8" placeholder="请输入文章内容" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="articleForm.isPublished" active-text="发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveArticle" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('articles')
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)

const articleList = ref<any[]>([])
const categories = ref<any[]>([])

const articleForm = reactive({
  id: 0,
  title: '',
  category: '',
  summary: '',
  content: '',
  isPublished: false,
})

const categoryMap: Record<string, string> = {
  emotion: '情绪管理',
  stress: '压力调节',
  relationship: '人际关系',
  study: '学习心理',
  growth: '自我成长',
}

function getCategoryName(key: string) {
  return categoryMap[key] || key
}

function formatTime(time: string) {
  if (!time) return ''
  return time.replace('T', ' ').substring(0, 19)
}

async function fetchCategories() {
  try {
    const res = await fetch('http://localhost:9000/ai/articles/categories')
    if (res.ok) {
      categories.value = await res.json()
    }
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

async function fetchArticles() {
  loading.value = true
  try {
    const res = await fetch('http://localhost:9000/ai/articles')
    if (res.ok) {
      articleList.value = await res.json()
    }
  } catch (e) {
    console.error('加载文章列表失败', e)
    ElMessage.error('加载文章列表失败')
  } finally {
    loading.value = false
  }
}

function handleTabChange(tab: string) {
  if (tab === 'articles') {
    fetchArticles()
  }
}

function showCreateDialog() {
  isEdit.value = false
  Object.assign(articleForm, {
    id: 0,
    title: '',
    category: '',
    summary: '',
    content: '',
    isPublished: false,
  })
  dialogVisible.value = true
}

function editArticle(row: any) {
  isEdit.value = true
  Object.assign(articleForm, {
    id: row.id,
    title: row.title,
    category: row.category,
    summary: row.summary || '',
    content: row.content || '',
    isPublished: row.isPublished,
  })
  dialogVisible.value = true
}

async function deleteArticle(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
      type: 'warning',
    })
    const res = await fetch(`http://localhost:9000/ai/articles/${id}`, {
      method: 'DELETE',
    })
    if (res.ok) {
      ElMessage.success('删除成功')
      fetchArticles()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function saveArticle() {
  if (!articleForm.title || !articleForm.category || !articleForm.content) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  saving.value = true
  try {
    const url = isEdit.value 
      ? `http://localhost:9000/ai/articles/${articleForm.id}`
      : 'http://localhost:9000/ai/articles'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const body: any = {
      title: articleForm.title,
      category: articleForm.category,
      summary: articleForm.summary,
      content: articleForm.content,
      is_published: articleForm.isPublished,
    }
    
    if (isEdit.value) {
      delete body.is_published
    }
    
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    
    if (res.ok) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      fetchArticles()
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchArticles()
})
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
