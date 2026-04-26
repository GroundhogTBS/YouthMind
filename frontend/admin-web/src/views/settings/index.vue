<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="预警阈值" name="threshold">
          <el-form :model="thresholdForm" label-width="150px" style="max-width: 500px;">
            <el-form-item label="黄色预警阈值">
              <el-input-number v-model="thresholdForm.yellow" :min="0" :max="1" :step="0.1" :precision="2" />
            </el-form-item>
            <el-form-item label="橙色预警阈值">
              <el-input-number v-model="thresholdForm.orange" :min="0" :max="1" :step="0.1" :precision="2" />
            </el-form-item>
            <el-form-item label="红色预警阈值">
              <el-input-number v-model="thresholdForm.red" :min="0" :max="1" :step="0.1" :precision="2" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveThreshold">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通知设置" name="notification">
          <el-form :model="notificationForm" label-width="150px" style="max-width: 500px;">
            <el-form-item label="预警通知管理员">
              <el-switch v-model="notificationForm.notifyAdmin" />
            </el-form-item>
            <el-form-item label="短信通知">
              <el-switch v-model="notificationForm.smsEnabled" />
            </el-form-item>
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationForm.emailEnabled" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotification">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="系统配置" name="system">
          <el-form :model="systemForm" label-width="150px" style="max-width: 500px;">
            <el-form-item label="会话最大时长">
              <el-input-number v-model="systemForm.maxSessionDuration" :min="10" :max="120" />
              <span style="margin-left: 8px;">分钟</span>
            </el-form-item>
            <el-form-item label="AI响应超时">
              <el-input-number v-model="systemForm.aiTimeout" :min="5" :max="60" />
              <span style="margin-left: 8px;">秒</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystem">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('threshold')

const thresholdForm = reactive({
  yellow: 0.3,
  orange: 0.6,
  red: 0.85,
})

const notificationForm = reactive({
  notifyAdmin: true,
  smsEnabled: true,
  emailEnabled: false,
})

const systemForm = reactive({
  maxSessionDuration: 60,
  aiTimeout: 30,
})

function saveThreshold() {
  ElMessage.success('预警阈值设置已保存')
}

function saveNotification() {
  ElMessage.success('通知设置已保存')
}

function saveSystem() {
  ElMessage.success('系统配置已保存')
}
</script>

<style lang="scss" scoped>
.settings-page {
  // styles
}
</style>
