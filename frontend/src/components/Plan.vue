<template>
    <div class="plan-container">
        <h2>今日饮食计划</h2>
        
        <div class="date-picker">
            <el-date-picker 
                v-model="selectedDate" 
                type="date" 
                placeholder="选择日期"
                @change="loadPlan"
            />
            <el-button type="primary" @click="regeneratePlan" :loading="loading">
                重新生成
            </el-button>
        </div>
        
        <el-row :gutter="20" v-if="plan">
            <el-col :span="8">
                <el-card class="meal-card breakfast">
                    <template #header>
                        <div class="card-header">
                            <span>🌅 早餐</span>
                            <span class="calories">{{ getMealCalories(plan.breakfast) }} 卡</span>
                        </div>
                    </template>
                    <div class="food-list">
                        <el-tag v-for="food in plan.breakfast" :key="food.id" class="food-tag">
                            {{ food.name }}
                        </el-tag>
                    </div>
                </el-card>
            </el-col>
            
            <el-col :span="8">
                <el-card class="meal-card lunch">
                    <template #header>
                        <div class="card-header">
                            <span>🌞 午餐</span>
                            <span class="calories">{{ getMealCalories(plan.lunch) }} 卡</span>
                        </div>
                    </template>
                    <div class="food-list">
                        <el-tag v-for="food in plan.lunch" :key="food.id" class="food-tag">
                            {{ food.name }}
                        </el-tag>
                    </div>
                </el-card>
            </el-col>
            
            <el-col :span="8">
                <el-card class="meal-card dinner">
                    <template #header>
                        <div class="card-header">
                            <span>🌙 晚餐</span>
                            <span class="calories">{{ getMealCalories(plan.dinner) }} 卡</span>
                        </div>
                    </template>
                    <div class="food-list">
                        <el-tag v-for="food in plan.dinner" :key="food.id" class="food-tag">
                            {{ food.name }}
                        </el-tag>
                    </div>
                </el-card>
            </el-col>
        </el-row>
        
        <div v-if="plan" class="total-calories">
            今日总热量：<strong>{{ plan.total_calories || getTotalCalories() }}</strong> 卡
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const loading = ref(false)
const selectedDate = ref(new Date())
const plan = ref(null)

const getMealCalories = (meal) => {
    return meal.reduce((sum, food) => sum + (food.calories || 0), 0)
}

const getTotalCalories = () => {
    if (!plan.value) return 0
    return getMealCalories(plan.value.breakfast) + 
           getMealCalories(plan.value.lunch) + 
           getMealCalories(plan.value.dinner)
}

const loadPlan = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    const dateStr = selectedDate.value.toISOString().split('T')[0]
    const res = await api.get(`/plan/${userData.id}?date=${dateStr}`)
    if (res.code === 200) {
        plan.value = res.data
    } else {
        ElMessage.error(res.message)
    }
}

const regeneratePlan = async () => {
    loading.value = true
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    const res = await api.post(`/plan/${userData.id}/regenerate`)
    loading.value = false
    if (res.code === 200) {
        plan.value = res.data
        ElMessage.success('已重新生成计划')
    } else {
        ElMessage.error(res.message)
    }
}

onMounted(() => {
    loadPlan()
})
</script>

<style scoped>
.plan-container {
    max-width: 1200px;
    margin: 0 auto;
}

.date-picker {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.meal-card {
    height: 100%;
}

.card-header {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
}

.calories {
    color: #e67e22;
}

.food-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.food-tag {
    font-size: 14px;
}

.total-calories {
    text-align: center;
    font-size: 18px;
    margin-top: 20px;
    padding: 15px;
    background: #f0f9f4;
    border-radius: 10px;
}
</style>