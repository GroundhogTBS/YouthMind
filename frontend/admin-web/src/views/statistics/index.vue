<template>
  <div class="statistics-page">
    <el-card>
      <template #header>
        <span>数据统计</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-container" ref="userTrendChartRef"></div>
        </el-col>
        <el-col :span="12">
          <div class="chart-container" ref="sessionTrendChartRef"></div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <div class="chart-container" ref="emotionDistChartRef"></div>
        </el-col>
        <el-col :span="12">
          <div class="chart-container" ref="assessmentChartRef"></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const userTrendChartRef = ref<HTMLElement>()
const sessionTrendChartRef = ref<HTMLElement>()
const emotionDistChartRef = ref<HTMLElement>()
const assessmentChartRef = ref<HTMLElement>()

onMounted(() => {
  if (userTrendChartRef.value) {
    const chart = echarts.init(userTrendChartRef.value)
    chart.setOption({
      title: { text: '用户增长趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value' },
      series: [{ type: 'line', data: [120, 200, 350, 480, 620, 800], smooth: true, areaStyle: {} }],
    })
  }
  
  if (sessionTrendChartRef.value) {
    const chart = echarts.init(sessionTrendChartRef.value)
    chart.setOption({
      title: { text: '对话会话趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [120, 200, 150, 180, 220, 280, 250] }],
    })
  }
  
  if (emotionDistChartRef.value) {
    const chart = echarts.init(emotionDistChartRef.value)
    chart.setOption({
      title: { text: '情绪分布' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 35, name: '开心' },
          { value: 25, name: '焦虑' },
          { value: 20, name: '难过' },
          { value: 15, name: '平静' },
          { value: 5, name: '其他' },
        ],
      }],
    })
  }
  
  if (assessmentChartRef.value) {
    const chart = echarts.init(assessmentChartRef.value)
    chart.setOption({
      title: { text: '测评完成情况' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['PHQ-9', 'GAD-7', 'PSS-10'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [450, 380, 220] }],
    })
  }
})
</script>

<style lang="scss" scoped>
.statistics-page {
  .chart-container {
    height: 300px;
  }
}
</style>
