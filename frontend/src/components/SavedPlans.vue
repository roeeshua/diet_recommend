<template>
    <div class="saved-plans-container">
        <div class="header">
            <h2>📋 我的计划库</h2>
            <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                自定义计划
            </el-button>
        </div>
        
        <div class="plan-count">
            已保存 {{ plans.length }} / 10 个计划
        </div>
        
        <div class="plans-grid" v-if="plans.length">
            <el-card v-for="plan in plans" :key="plan.id" class="plan-card">
                <template #header>
                    <div class="card-header">
                        <span class="plan-name">🍱 {{ plan.plan_name }}</span>
                        <div class="card-actions">
                            <el-button type="success" size="small" @click="checkinPlan(plan)">
                                <el-icon><Checked /></el-icon>
                                一键打卡
                            </el-button>
                            <el-button type="danger" size="small" @click="deletePlan(plan.id)">
                                <el-icon><Delete /></el-icon>
                                删除
                            </el-button>
                        </div>
                    </div>
                </template>
                
                <div class="meal-section">
                    <div class="meal-label">🌅 早餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in plan.foods.breakfast" :key="idx" size="small">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                        <span v-if="!plan.foods.breakfast?.length" class="empty">暂无</span>
                    </div>
                </div>
                
                <div class="meal-section">
                    <div class="meal-label">🌞 午餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in plan.foods.lunch" :key="idx" size="small" type="success">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                        <span v-if="!plan.foods.lunch?.length" class="empty">暂无</span>
                    </div>
                </div>
                
                <div class="meal-section">
                    <div class="meal-label">🌙 晚餐</div>
                    <div class="food-tags">
                        <el-tag v-for="(food, idx) in plan.foods.dinner" :key="idx" size="small" type="warning">
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                        <span v-if="!plan.foods.dinner?.length" class="empty">暂无</span>
                    </div>
                </div>
                
                <div class="plan-footer">
                    <span class="total-calories">🔥 总热量：{{ plan.total_calories }} 卡</span>
                    <span class="created-at">📅 创建于：{{ formatDate(plan.created_at) }}</span>
                </div>
            </el-card>
        </div>
        
        <el-empty v-else description="暂无计划，先去「饮食计划」页面生成并保存吧" />
        
        <!-- 自定义计划弹窗 -->
        <el-dialog v-model="showCreateDialog" title="自定义计划" width="800px">
            <el-form :model="customPlan" label-width="100px">
                <el-form-item label="计划名称" required>
                    <el-input v-model="customPlan.plan_name" placeholder="如：健身增肌餐" />
                </el-form-item>
                
                <el-divider>早餐</el-divider>
                <div class="meal-editor">
                    <div class="food-selector">
                        <el-select
                            v-model="selectedFoodId.breakfast"
                            filterable
                            remote
                            reserve-keyword
                            placeholder="搜索并选择食物"
                            :remote-method="(q) => searchFoods(q, 'breakfast')"
                            :loading="searchLoading"
                            style="width: 70%"
                            @change="(val) => addFood('breakfast', val)"
                        >
                            <el-option
                                v-for="food in searchResults.breakfast"
                                :key="food.id"
                                :label="`${food.name} (${food.calories}卡)`"
                                :value="food.id"
                            />
                        </el-select>
                        <el-button type="primary" plain @click="openCustomFood('breakfast')">
                            自定义食物
                        </el-button>
                    </div>
                    <div class="selected-foods">
                        <el-tag
                            v-for="(food, idx) in customPlan.breakfast"
                            :key="idx"
                            closable
                            @close="removeFood('breakfast', idx)"
                        >
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <el-divider>午餐</el-divider>
                <div class="meal-editor">
                    <div class="food-selector">
                        <el-select
                            v-model="selectedFoodId.lunch"
                            filterable
                            remote
                            reserve-keyword
                            placeholder="搜索并选择食物"
                            :remote-method="(q) => searchFoods(q, 'lunch')"
                            :loading="searchLoading"
                            style="width: 70%"
                            @change="(val) => addFood('lunch', val)"
                        >
                            <el-option
                                v-for="food in searchResults.lunch"
                                :key="food.id"
                                :label="`${food.name} (${food.calories}卡)`"
                                :value="food.id"
                            />
                        </el-select>
                        <el-button type="primary" plain @click="openCustomFood('lunch')">
                            自定义食物
                        </el-button>
                    </div>
                    <div class="selected-foods">
                        <el-tag
                            v-for="(food, idx) in customPlan.lunch"
                            :key="idx"
                            closable
                            @close="removeFood('lunch', idx)"
                            type="success"
                        >
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <el-divider>晚餐</el-divider>
                <div class="meal-editor">
                    <div class="food-selector">
                        <el-select
                            v-model="selectedFoodId.dinner"
                            filterable
                            remote
                            reserve-keyword
                            placeholder="搜索并选择食物"
                            :remote-method="(q) => searchFoods(q, 'dinner')"
                            :loading="searchLoading"
                            style="width: 70%"
                            @change="(val) => addFood('dinner', val)"
                        >
                            <el-option
                                v-for="food in searchResults.dinner"
                                :key="food.id"
                                :label="`${food.name} (${food.calories}卡)`"
                                :value="food.id"
                            />
                        </el-select>
                        <el-button type="primary" plain @click="openCustomFood('dinner')">
                            自定义食物
                        </el-button>
                    </div>
                    <div class="selected-foods">
                        <el-tag
                            v-for="(food, idx) in customPlan.dinner"
                            :key="idx"
                            closable
                            @close="removeFood('dinner', idx)"
                            type="warning"
                        >
                            {{ food.name }} ({{ food.calories }}卡)
                        </el-tag>
                    </div>
                </div>
                
                <div class="total-calories-preview">
                    预估总热量：{{ calculateTotalCalories() }} 卡
                </div>
            </el-form>
            
            <template #footer>
                <el-button @click="showCreateDialog = false">取消</el-button>
                <el-button type="primary" @click="saveCustomPlan" :loading="saving">
                    保存计划
                </el-button>
            </template>
        </el-dialog>
        
        <!-- 自定义食物弹窗 -->
        <el-dialog v-model="showCustomFoodDialog" title="自定义食物" width="700px">
            <el-form :model="customFood" label-width="100px">
                <el-form-item label="食物名称" required>
                    <el-input v-model="customFood.name" />
                </el-form-item>
                <el-form-item label="类别">
                    <el-select v-model="customFood.category">
                        <el-option label="主食" value="主食" />
                        <el-option label="蛋白质" value="蛋白质" />
                        <el-option label="蔬菜" value="蔬菜" />
                        <el-option label="水果" value="水果" />
                    </el-select>
                </el-form-item>
                <el-form-item label="卡路里">
                    <el-input-number v-model="customFood.calories" :min="0" :max="2000" />
                </el-form-item>
                <el-form-item label="季节">
                    <el-select v-model="customFood.season">
                        <el-option label="春季" value="春季" />
                        <el-option label="夏季" value="夏季" />
                        <el-option label="秋季" value="秋季" />
                        <el-option label="冬季" value="冬季" />
                        <el-option label="四季" value="四季" />
                    </el-select>
                </el-form-item>
                <el-form-item label="标签">
                    <el-input v-model="customFood.tags" placeholder="多个标签用逗号分隔" />
                </el-form-item>
                
                <el-divider>营养指标（十分制）</el-divider>
                <el-row :gutter="15">
                    <el-col :span="8">
                        <el-form-item label="蛋白质">
                            <el-slider v-model="customFood.protein" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="膳食纤维">
                            <el-slider v-model="customFood.fiber" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="微量元素">
                            <el-slider v-model="customFood.vitamins" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-row :gutter="15">
                    <el-col :span="8">
                        <el-form-item label="添加糖">
                            <el-slider v-model="customFood.sugar" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="饱和脂肪">
                            <el-slider v-model="customFood.saturated_fat" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                    <el-col :span="8">
                        <el-form-item label="钠">
                            <el-slider v-model="customFood.sodium" :min="1" :max="10" />
                        </el-form-item>
                    </el-col>
                </el-row>
                
                <el-divider>饮食特征（可多选）</el-divider>
                <el-form-item label="特征标签">
                    <el-select
                        v-model="customFood.features"
                        multiple
                        filterable
                        allow-create
                        default-first-option
                        placeholder="选择或输入特征"
                        style="width: 100%"
                    >
                        <el-option
                            v-for="feature in featureOptions"
                            :key="feature"
                            :label="feature"
                            :value="feature"
                        />
                    </el-select>
                    <div class="feature-hint">提示：支持自定义输入新特征</div>
                </el-form-item>
                
                <el-button type="success" @click="aiFillFood" :loading="aiLoading">
                    🤖 AI 自动补全（输入食物名称后点击）
                </el-button>
            </el-form>
            
            <template #footer>
                <el-button @click="showCustomFoodDialog = false">取消</el-button>
                <el-button type="primary" @click="addCustomFood">添加</el-button>
            </template>
        </el-dialog>
        
        <!-- 一键打卡日期选择弹窗 -->
        <el-dialog v-model="showCheckinDialog" title="选择打卡日期" width="400px">
            <el-date-picker
                v-model="checkinDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
            />
            <template #footer>
                <el-button @click="showCheckinDialog = false">取消</el-button>
                <el-button type="primary" @click="confirmCheckin" :loading="checkinLoading">
                    确认打卡
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Checked } from '@element-plus/icons-vue'
import api from '../api'

const checkinDate = ref('')
const userData = JSON.parse(localStorage.getItem('user') || '{}')
const plans = ref([])
const allFoods = ref([])
const saving = ref(false)
const checkinLoading = ref(false)
const searchLoading = ref(false)
const aiLoading = ref(false)
const showCreateDialog = ref(false)
const showCustomFoodDialog = ref(false)
const showCheckinDialog = ref(false)
let currentCheckinPlan = null
let currentMealType = 'breakfast'

// 预设特征选项（24种）
const featureOptions = [
    '辣味', '麻辣', '酸味', '甜味', '咸鲜', '清淡', '浓郁', '清爽',
    '高蛋白', '低脂', '低碳水', '高纤维', '高钙', '低卡', '高维生素', '均衡营养',
    '海鲜', '红肉', '白肉', '素食', '抗氧化', '助消化', '补气血', '增强免疫'
]

const customPlan = ref({
    plan_name: '',
    breakfast: [],
    lunch: [],
    dinner: []
})

const selectedFoodId = ref({
    breakfast: null,
    lunch: null,
    dinner: null
})

const searchResults = ref({
    breakfast: [],
    lunch: [],
    dinner: []
})

const customFood = ref({
    name: '',
    category: '',
    calories: 0,
    season: '四季',
    tags: '',
    features: [],
    protein: 5,
    fiber: 5,
    vitamins: 5,
    sugar: 5,
    saturated_fat: 5,
    sodium: 5
})

// 获取所有食物
const loadFoods = async () => {
    const res = await api.get('/foods')
    if (res.code === 200) {
        allFoods.value = res.data
    }
}

// 获取用户计划
const loadPlans = async () => {
    const res = await api.get(`/plan/list/${userData.id}`)
    if (res.code === 200) {
        plans.value = res.data
    }
}

// 搜索食物
const searchFoods = async (query, mealType) => {
    if (!query) {
        searchResults.value[mealType] = []
        return
    }
    searchLoading.value = true
    const res = await api.get('/foods')
    searchLoading.value = false
    if (res.code === 200) {
        searchResults.value[mealType] = res.data.filter(f => 
            f.name.toLowerCase().includes(query.toLowerCase())
        )
    }
}

// 添加食物
const addFood = (mealType, foodId) => {
    const food = allFoods.value.find(f => f.id === foodId)
    if (food && !customPlan.value[mealType].find(f => f.id === foodId)) {
        customPlan.value[mealType].push(food)
    }
    selectedFoodId.value[mealType] = null
}

// 移除食物
const removeFood = (mealType, index) => {
    customPlan.value[mealType].splice(index, 1)
}

// 打开自定义食物弹窗
const openCustomFood = (mealType) => {
    currentMealType = mealType
    customFood.value = {
        name: '',
        category: '',
        calories: 0,
        season: '四季',
        tags: '',
        features: [],
        protein: 5,
        fiber: 5,
        vitamins: 5,
        sugar: 5,
        saturated_fat: 5,
        sodium: 5
    }
    showCustomFoodDialog.value = true
}

// AI 自动补全
const aiFillFood = async () => {
    if (!customFood.value.name) {
        ElMessage.warning('请先输入食物名称')
        return
    }
    
    aiLoading.value = true
    try {
        const res = await api.post('/ai/fill_food', {
            food_name: customFood.value.name
        })
        if (res.code === 200) {
            const data = res.data
            customFood.value.category = data.category || ''
            customFood.value.calories = data.calories || 0
            customFood.value.season = data.season || '四季'
            customFood.value.tags = data.tags || ''
            customFood.value.features = data.features || []
            customFood.value.protein = data.protein || 5
            customFood.value.fiber = data.fiber || 5
            customFood.value.vitamins = data.vitamins || 5
            customFood.value.sugar = data.sugar || 5
            customFood.value.saturated_fat = data.saturated_fat || 5
            customFood.value.sodium = data.sodium || 5
            ElMessage.success('AI 补全成功')
        } else {
            ElMessage.error(res.message || 'AI 补全失败')
        }
    } catch (error) {
        console.error('AI 补全失败:', error)
        ElMessage.error('AI 补全失败，请稍后重试')
    } finally {
        aiLoading.value = false
    }
}

// 添加自定义食物
const addCustomFood = () => {
    if (!customFood.value.name) {
        ElMessage.warning('请填写食物名称')
        return
    }
    // 复制完整食物对象，包含 features
    customPlan.value[currentMealType].push({ ...customFood.value })
    showCustomFoodDialog.value = false
}

// 计算总热量
const calculateTotalCalories = () => {
    let total = 0
    for (const meal of ['breakfast', 'lunch', 'dinner']) {
        for (const food of customPlan.value[meal]) {
            total += food.calories || 0
        }
    }
    return total
}

// 保存自定义计划
const saveCustomPlan = async () => {
    if (!customPlan.value.plan_name) {
        ElMessage.warning('请输入计划名称')
        return
    }
    
    const totalCalories = calculateTotalCalories()
    
    saving.value = true
    const res = await api.post('/plan/save', {
        user_id: userData.id,
        plan_name: customPlan.value.plan_name,
        foods: {
            breakfast: customPlan.value.breakfast,
            lunch: customPlan.value.lunch,
            dinner: customPlan.value.dinner
        },
        total_calories: totalCalories
    })
    saving.value = false
    
    if (res.code === 200) {
        ElMessage.success('计划保存成功')
        showCreateDialog.value = false
        customPlan.value = {
            plan_name: '',
            breakfast: [],
            lunch: [],
            dinner: []
        }
        loadPlans()
    } else {
        ElMessage.error(res.message)
    }
}

// 删除计划
const deletePlan = async (planId) => {
    ElMessageBox.confirm('确定删除这个计划吗？', '提示', { type: 'warning' }).then(async () => {
        const res = await api.delete(`/plan/${planId}?user_id=${userData.id}`)
        if (res.code === 200) {
            ElMessage.success('删除成功')
            loadPlans()
        } else {
            ElMessage.error(res.message)
        }
    }).catch(() => {})
}

// 一键打卡
const checkinPlan = (plan) => {
    currentCheckinPlan = plan
    showCheckinDialog.value = true
}

const confirmCheckin = async () => {
    if (!checkinDate.value) {
        ElMessage.warning('请选择打卡日期')
        return
    }
    
    checkinLoading.value = true
    const res = await api.post(`/plan/checkin/${currentCheckinPlan.id}`, {
        user_id: userData.id,
        date: checkinDate.value
    })
    checkinLoading.value = false
    
    if (res.code === 200) {
        ElMessage.success(res.message)
        showCheckinDialog.value = false
        checkinDate.value = ''
    } else {
        ElMessage.error(res.message)
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return dateStr.split('T')[0]
}

onMounted(() => {
    loadFoods()
    loadPlans()
})
</script>

<style scoped>
.saved-plans-container {
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.plan-count {
    color: #666;
    margin-bottom: 20px;
    font-size: 14px;
}

.plans-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.plan-card {
    border-radius: 12px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.plan-name {
    font-size: 18px;
    font-weight: bold;
    color: #e67e22;
}

.card-actions {
    display: flex;
    gap: 10px;
}

.meal-section {
    margin-bottom: 15px;
}

.meal-label {
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
}

.food-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.empty {
    color: #999;
    font-size: 12px;
}

.plan-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #eee;
    color: #666;
    font-size: 13px;
}

.total-calories {
    color: #e67e22;
    font-weight: bold;
}

.meal-editor {
    margin-bottom: 15px;
}

.food-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.selected-foods {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.total-calories-preview {
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    color: #e67e22;
    margin-top: 20px;
}

.feature-hint {
    font-size: 12px;
    color: #999;
    margin-top: 5px;
}
</style>