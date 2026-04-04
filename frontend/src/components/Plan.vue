<template>
    <div class="plan-container">
        <h2>饮食计划</h2>
        <p class="desc">AI 会根据你的个人信息和饮食偏好，为你生成个性化饮食计划</p>
        
        <div class="actions">
            <el-button type="primary" @click="generatePlan" :loading="generating">
                🤖 生成今日计划
            </el-button>
            <el-button type="success" @click="regeneratePlan" :loading="generating" plain>
                🔄 换一批
            </el-button>
        </div>
        
        <div v-if="currentPlan" class="plan-result">
            <el-card class="plan-card">
                <template #header>
                    <div class="card-header">
                        <span>🍱 AI 推荐计划</span>
                        <div class="card-actions">
                            <el-input
                                v-model="planName"
                                placeholder="计划名称"
                                style="width: 150px; margin-right: 10px"
                                size="small"
                            />
                            <el-button type="success" size="small" @click="savePlan" :loading="saving">
                                保存到计划库
                            </el-button>
                        </div>
                    </div>
                </template>
                
                <div class="meal-section">
                    <div class="meal-label">🌅 早餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in currentPlan.breakfast" :key="idx" size="small">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <div class="meal-section">
                    <div class="meal-label">🌞 午餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in currentPlan.lunch" :key="idx" size="small" type="success">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <div class="meal-section">
                    <div class="meal-label">🌙 晚餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in currentPlan.dinner" :key="idx" size="small" type="warning">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <div class="plan-footer">
                    <span class="total-calories">🔥 总热量：{{ currentPlan.total_calories }} 卡</span>
                </div>
            </el-card>
        </div>
        
        <el-empty v-else description="点击「生成今日计划」获取 AI 推荐" />
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const userData = JSON.parse(localStorage.getItem('user') || '{}')
const generating = ref(false)
const saving = ref(false)
const currentPlan = ref(null)
const planName = ref('')

const generatePlan = async () => {
    generating.value = true
    const res = await api.post('/plan/generate', { user_id: userData.id })
    generating.value = false
    
    if (res.code === 200) {
        currentPlan.value = res.data
        planName.value = `AI计划${new Date().toLocaleDateString()}`
        ElMessage.success('计划生成成功')
    } else {
        ElMessage.error(res.message)
    }
}

// 添加 regeneratePlan 方法（复用 generatePlan 逻辑）
const regeneratePlan = () => {
    generatePlan()  // 直接复用，重新调用接口
}

const savePlan = async () => {
    if (!planName.value) {
        ElMessage.warning('请输入计划名称')
        return
    }
    
    saving.value = true
    const res = await api.post('/plan/save', {
        user_id: userData.id,
        plan_name: planName.value,
        foods: {
            breakfast: currentPlan.value.breakfast,
            lunch: currentPlan.value.lunch,
            dinner: currentPlan.value.dinner
        },
        total_calories: currentPlan.value.total_calories
    })
    saving.value = false
    
    if (res.code === 200) {
        ElMessage.success('已保存到计划库')
    } else {
        ElMessage.error(res.message)
    }
}
</script>

<style scoped>
.plan-container {
    max-width: 800px;
    margin: 0 auto;
}

.desc {
    color: #666;
    margin-bottom: 20px;
}

.actions {
    text-align: center;
    margin-bottom: 30px;
}

.plan-card {
    border-radius: 12px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.meal-section {
    margin-bottom: 20px;
}

.meal-label {
    font-weight: bold;
    margin-bottom: 10px;
    font-size: 16px;
}

.food-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.plan-footer {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #eee;
    text-align: center;
}

.total-calories {
    font-size: 16px;
    font-weight: bold;
    color: #e67e22;
}
</style>