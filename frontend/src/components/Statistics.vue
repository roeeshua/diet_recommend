<template>
    <div class="statistics-container">
        <h2>营养统计</h2>
        
        <el-date-picker 
            v-model="selectedMonth" 
            type="month" 
            placeholder="选择月份"
            @change="loadStatistics"
        />
        
        <div class="stats-cards" v-if="stats">
            <el-row :gutter="20">
                <el-col :span="8">
                    <el-card>
                        <div class="stat-number">{{ stats.total_days || 0 }}</div>
                        <div class="stat-label">总天数</div>
                    </el-card>
                </el-col>
                <el-col :span="8">
                    <el-card>
                        <div class="stat-number">{{ stats.checkin_days || 0 }}</div>
                        <div class="stat-label">打卡天数</div>
                    </el-card>
                </el-col>
                <el-col :span="8">
                    <el-card>
                        <div class="stat-number">{{ stats.checkin_rate || 0 }}%</div>
                        <div class="stat-label">打卡率</div>
                    </el-card>
                </el-col>
            </el-row>
        </div>
        
        <div class="chart-container" v-if="chartData.length">
            <h3>每日热量摄入趋势</h3>
            <div id="calories-chart" style="height: 400px;"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const selectedMonth = ref(new Date())
const stats = ref(null)
const chartData = ref([])
let chart = null

const userData = JSON.parse(localStorage.getItem('user') || '{}')

const loadStatistics = async () => {
    const year = selectedMonth.value.getFullYear()
    const month = selectedMonth.value.getMonth() + 1
    const res = await api.get(`/statistics/${userData.id}?month=${year}-${month}`)
    if (res.code === 200) {
        stats.value = res.data
        chartData.value = res.data.daily_calories || []
        renderChart()
    }
}

const renderChart = () => {
    nextTick(() => {
        const dom = document.getElementById('calories-chart')
        if (!dom) return
        
        if (chart) {
            chart.dispose()
        }
        
        chart = echarts.init(dom)
        chart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'category', data: chartData.value.map(d => d.date) },
            yAxis: { type: 'value', name: '热量(卡)' },
            series: [{
                data: chartData.value.map(d => d.calories),
                type: 'line',
                smooth: true,
                areaStyle: { opacity: 0.3 },
                lineStyle: { color: '#667eea', width: 3 },
                itemStyle: { color: '#667eea' }
            }]
        })
    })
}

onMounted(() => {
    loadStatistics()
})
</script>

<style scoped>
.statistics-container {
    max-width: 800px;
    margin: 0 auto;
}

.stat-number {
    font-size: 32px;
    font-weight: bold;
    color: #667eea;
    text-align: center;
}

.stat-label {
    text-align: center;
    color: #666;
    margin-top: 10px;
}

.chart-container {
    margin-top: 30px;
}
</style>