<template>
    <div class="statistics-container">
        <h2>营养统计</h2>
        
        <div class="controls">
            <el-date-picker 
                v-model="selectedMonth" 
                type="month" 
                placeholder="选择月份"
                format="YYYY年MM月"
                value-format="YYYY-MM"
                @change="loadStatistics"
            />
        </div>
        
        <!-- 折线图（7条线） -->
        <div class="chart-container" v-if="trendData.length">
            <div id="nutrients-chart" style="height: 500px;"></div>
        </div>
        
        <!-- 点击日期提示 -->
        <el-dialog v-model="showAdviceDialog" :title="`${selectedDate} 营养分析`" width="500px">
            <div v-if="dailyAdvice" class="advice-content">
                <div class="advice-item" :class="getAdviceClass(advice.calories)">
                    🔥 热量：{{ advice.calories }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.protein)">
                    🥩 蛋白质：{{ advice.protein }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.fiber)">
                    🌾 膳食纤维：{{ advice.fiber }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.vitamins)">
                    🍊 微量元素：{{ advice.vitamins }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.sugar, true)">
                    🍬 添加糖：{{ advice.sugar }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.saturated_fat, true)">
                    🥓 饱和脂肪：{{ advice.saturated_fat }}
                </div>
                <div class="advice-item" :class="getAdviceClass(advice.sodium, true)">
                    🧂 钠：{{ advice.sodium }}
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const userData = JSON.parse(localStorage.getItem('user') || '{}')
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const trendData = ref([])
const showAdviceDialog = ref(false)
const selectedDate = ref('')
const dailyAdvice = ref(null)

let chart = null

const getAdviceClass = (advice, isNegative = false) => {
    if (!advice) return ''
    if (advice.includes('正常')) return 'normal'
    if (isNegative && advice.includes('偏高')) return 'high'
    if (advice.includes('不足') || advice.includes('偏低')) return 'low'
    if (advice.includes('偏高')) return 'high'
    return ''
}

const loadStatistics = async () => {
    const [year, month] = selectedMonth.value.split('-')
    const res = await api.get(`/statistics/${userData.id}/monthly`, {
        params: { year, month }
    })
    if (res.code === 200) {
        trendData.value = res.data
        await nextTick()
        renderChart()
    }
}

const renderChart = () => {
    const dom = document.getElementById('nutrients-chart')
    if (!dom) return
    
    if (chart) chart.dispose()
    chart = echarts.init(dom)
    
    const dates = trendData.value.map(d => d.date.slice(5))
    
    const option = {
        title: { text: '每日营养趋势', left: 'center' },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['总热量(卡)', '蛋白质', '膳食纤维', '微量元素', '添加糖', '饱和脂肪', '钠'], top: 30 },
        grid: { left: '5%', right: '5%', top: '15%', bottom: '5%', containLabel: true },
        xAxis: { type: 'category', data: dates, name: '日期' },
        yAxis: [
            { type: 'value', name: '热量(卡)', position: 'left' },
            { type: 'value', name: '营养评分', position: 'right', min: 0, max: 100 }
        ],
        series: [
            { name: '总热量(卡)', type: 'line', data: trendData.value.map(d => d.total_calories), yAxisIndex: 0, smooth: true, lineStyle: { color: '#ff6b6b', width: 3 }, symbol: 'circle', symbolSize: 8 },
            { name: '蛋白质', type: 'line', data: trendData.value.map(d => d.protein), yAxisIndex: 1, smooth: true, lineStyle: { color: '#4ecdc4' } },
            { name: '膳食纤维', type: 'line', data: trendData.value.map(d => d.fiber), yAxisIndex: 1, smooth: true, lineStyle: { color: '#45b7d1' } },
            { name: '微量元素', type: 'line', data: trendData.value.map(d => d.vitamins), yAxisIndex: 1, smooth: true, lineStyle: { color: '#96ceb4' } },
            { name: '添加糖', type: 'line', data: trendData.value.map(d => d.sugar), yAxisIndex: 1, smooth: true, lineStyle: { color: '#feca57' } },
            { name: '饱和脂肪', type: 'line', data: trendData.value.map(d => d.saturated_fat), yAxisIndex: 1, smooth: true, lineStyle: { color: '#ff9f43' } },
            { name: '钠', type: 'line', data: trendData.value.map(d => d.sodium), yAxisIndex: 1, smooth: true, lineStyle: { color: '#eccc68' } }
        ]
    }
    
    chart.setOption(option)
    
    // 点击事件
    chart.off('click')
    chart.on('click', async (params) => {
        if (params.componentType === 'series') {
            const clickedDate = trendData.value[params.dataIndex].date
            selectedDate.value = clickedDate
            const res = await api.get(`/statistics/${userData.id}/${clickedDate}`)
            if (res.code === 200) {
                dailyAdvice.value = res.data
                showAdviceDialog.value = true
            }
        }
    })
}

watch(selectedMonth, () => loadStatistics())

onMounted(() => {
    loadStatistics()
    window.addEventListener('resize', () => chart?.resize())
})
</script>

<style scoped>
.statistics-container {
    max-width: 1200px;
    margin: 0 auto;
}

.controls {
    margin-bottom: 20px;
    text-align: center;
}

.chart-container {
    background: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.advice-content {
    padding: 10px;
}

.advice-item {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 8px;
    background: #f5f7fa;
}

.advice-item.normal {
    background: #d4edda;
    color: #155724;
}

.advice-item.high {
    background: #f8d7da;
    color: #721c24;
}

.advice-item.low {
    background: #fff3cd;
    color: #856404;
}
</style>