<template>
    <div class="checkin-container">
        <h2>饮食打卡</h2>
        
        <!-- 日期选择器 -->
        <div class="date-selector">
            <el-date-picker 
                v-model="selectedDate" 
                type="date" 
                placeholder="选择日期"
                @change="loadMeals"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
            />
        </div>
        
        <!-- 三餐打卡区域 -->
        <div class="meals-container">
            <el-row :gutter="20">
                <el-col :span="8">
                    <el-card class="meal-card">
                        <template #header>
                            <div class="card-header">
                                <span>🌅 早餐</span>
                                <el-button type="primary" size="small" @click="openAddDialog('breakfast')">
                                    添加
                                </el-button>
                            </div>
                        </template>
                        <div class="meal-list">
                            <div v-for="(item, idx) in meals.breakfast" :key="idx" class="meal-item">
                                <span>{{ item.food_name }}</span>
                                <span class="calories">{{ item.calories }}卡</span>
                                <el-icon @click="deleteMeal(item.id)" class="delete-icon"><Close /></el-icon>
                            </div>
                            <div v-if="!meals.breakfast.length" class="empty">暂无记录</div>
                        </div>
                    </el-card>
                </el-col>
                
                <el-col :span="8">
                    <el-card class="meal-card">
                        <template #header>
                            <div class="card-header">
                                <span>🌞 午餐</span>
                                <el-button type="primary" size="small" @click="openAddDialog('lunch')">
                                    添加
                                </el-button>
                            </div>
                        </template>
                        <div class="meal-list">
                            <div v-for="(item, idx) in meals.lunch" :key="idx" class="meal-item">
                                <span>{{ item.food_name }}</span>
                                <span class="calories">{{ item.calories }}卡</span>
                                <el-icon @click="deleteMeal(item.id)" class="delete-icon"><Close /></el-icon>
                            </div>
                            <div v-if="!meals.lunch.length" class="empty">暂无记录</div>
                        </div>
                    </el-card>
                </el-col>
                
                <el-col :span="8">
                    <el-card class="meal-card">
                        <template #header>
                            <div class="card-header">
                                <span>🌙 晚餐</span>
                                <el-button type="primary" size="small" @click="openAddDialog('dinner')">
                                    添加
                                </el-button>
                            </div>
                        </template>
                        <div class="meal-list">
                            <div v-for="(item, idx) in meals.dinner" :key="idx" class="meal-item">
                                <span>{{ item.food_name }}</span>
                                <span class="calories">{{ item.calories }}卡</span>
                                <el-icon @click="deleteMeal(item.id)" class="delete-icon"><Close /></el-icon>
                            </div>
                            <div v-if="!meals.dinner.length" class="empty">暂无记录</div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>
        
        <!-- 添加食物弹窗 -->
        <el-dialog v-model="showAddDialog" :title="`添加${mealTypeMap[currentMealType]}`" width="700px">
            <el-form :model="foodForm" label-width="100px">
                <el-form-item label="选择食物">
                    <el-select
                        v-model="selectedFoodId"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="输入关键词搜索食物"
                        :remote-method="searchFoods"
                        :loading="searchLoading"
                        style="width: 100%"
                        @change="onFoodSelect"
                    >
                        <el-option
                            v-for="food in searchResults"
                            :key="food.id"
                            :label="`${food.name} (${food.category}) ${food.calories}卡`"
                            :value="food.id"
                        />
                    </el-select>
                </el-form-item>
                
                <el-divider>或自定义食物</el-divider>
                
                <el-button type="primary" plain @click="showCustomForm = !showCustomForm">
                    {{ showCustomForm ? '收起' : '填写自定义食物' }}
                </el-button>
                
                <div v-show="showCustomForm" class="custom-form">
                    <el-row :gutter="15">
                        <el-col :span="12">
                            <el-form-item label="食物名称">
                                <el-input v-model="foodForm.food_name" placeholder="必填" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="类别">
                                <el-select v-model="foodForm.category" placeholder="请选择">
                                    <el-option label="主食" value="主食" />
                                    <el-option label="蛋白质" value="蛋白质" />
                                    <el-option label="蔬菜" value="蔬菜" />
                                    <el-option label="水果" value="水果" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-row :gutter="15">
                        <el-col :span="12">
                            <el-form-item label="卡路里">
                                <el-input-number v-model="foodForm.calories" :min="0" :max="2000" style="width: 100%" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="季节">
                                <el-select v-model="foodForm.season">
                                    <el-option label="春季" value="春季" />
                                    <el-option label="夏季" value="夏季" />
                                    <el-option label="秋季" value="秋季" />
                                    <el-option label="冬季" value="冬季" />
                                    <el-option label="四季" value="四季" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-form-item label="标签">
                        <el-input v-model="foodForm.tags" placeholder="多个标签用逗号分隔" />
                    </el-form-item>
                    
                    <el-divider>营养指标（十分制）</el-divider>
                    
                    <el-row :gutter="15">
                        <el-col :span="8">
                            <el-form-item label="蛋白质">
                                <el-slider v-model="foodForm.protein" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="膳食纤维">
                                <el-slider v-model="foodForm.fiber" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="微量元素">
                                <el-slider v-model="foodForm.vitamins" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-row :gutter="15">
                        <el-col :span="8">
                            <el-form-item label="添加糖">
                                <el-slider v-model="foodForm.sugar" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="饱和脂肪">
                                <el-slider v-model="foodForm.saturated_fat" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                        <el-col :span="8">
                            <el-form-item label="钠">
                                <el-slider v-model="foodForm.sodium" :min="1" :max="10" show-stops />
                            </el-form-item>
                        </el-col>
                    </el-row>
                    
                    <el-button type="success" size="small" @click="autoFillByAI" :loading="aiLoading">
                        🤖 AI 自动补全（输入食物名称后点击）
                    </el-button>
                </div>
            </el-form>
            
            <template #footer>
                <el-button @click="showAddDialog = false">取消</el-button>
                <el-button type="primary" @click="submitMeal">提交</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import api from '../api'

const userData = JSON.parse(localStorage.getItem('user') || '{}')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const meals = reactive({ breakfast: [], lunch: [], dinner: [] })

// 弹窗相关
const showAddDialog = ref(false)
const currentMealType = ref('breakfast')
const mealTypeMap = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' }
const showCustomForm = ref(false)
const selectedFoodId = ref(null)
const searchResults = ref([])
const searchLoading = ref(false)
const aiLoading = ref(false)

// 自定义食物表单
const foodForm = reactive({
    food_name: '',
    category: '',
    calories: 0,
    season: '',
    tags: '',
    protein: 5,
    fiber: 5,
    vitamins: 5,
    sugar: 5,
    saturated_fat: 5,
    sodium: 5
})

// 加载某天所有餐食
const loadMeals = async () => {
    const res = await api.get(`/checkin/${userData.id}/${selectedDate.value}`)
    if (res.code === 200) {
        meals.breakfast = res.data.filter(m => m.meal_type === 'breakfast')
        meals.lunch = res.data.filter(m => m.meal_type === 'lunch')
        meals.dinner = res.data.filter(m => m.meal_type === 'dinner')
    }
}

// 搜索食物
const searchFoods = async (query) => {
    if (!query) return
    searchLoading.value = true
    const res = await api.get('/foods')
    searchLoading.value = false
    if (res.code === 200) {
        searchResults.value = res.data.filter(f => 
            f.name.toLowerCase().includes(query.toLowerCase())
        )
    }
}

// 选择已有食物
const onFoodSelect = (foodId) => {
    const food = searchResults.value.find(f => f.id === foodId)
    if (food) {
        foodForm.food_name = food.name
        foodForm.category = food.category
        foodForm.calories = food.calories
        foodForm.season = food.season
        foodForm.tags = food.tags ? food.tags.join(',') : ''
        foodForm.protein = food.protein || 5
        foodForm.fiber = food.fiber || 5
        foodForm.vitamins = food.vitamins || 5
        foodForm.sugar = food.sugar || 5
        foodForm.saturated_fat = food.saturated_fat || 5
        foodForm.sodium = food.sodium || 5
        showCustomForm.value = true
    }
}

// AI 自动补全（通过后端代理）
const autoFillByAI = async () => {
    if (!foodForm.food_name) {
        ElMessage.warning('请先输入食物名称')
        return
    }
    
    aiLoading.value = true
    try {
        const res = await api.post('/ai/fill_food', {
            food_name: foodForm.food_name
        })
        
        if (res.code === 200) {
            const data = res.data
            foodForm.category = data.category || ''
            foodForm.calories = data.calories || 0
            foodForm.season = data.season || ''
            foodForm.tags = data.tags || ''
            foodForm.protein = data.protein || 5
            foodForm.fiber = data.fiber || 5
            foodForm.vitamins = data.vitamins || 5
            foodForm.sugar = data.sugar || 5
            foodForm.saturated_fat = data.saturated_fat || 5
            foodForm.sodium = data.sodium || 5
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

// 打开添加弹窗
const openAddDialog = (type) => {
    currentMealType.value = type
    showCustomForm.value = false
    selectedFoodId.value = null
    Object.assign(foodForm, {
        food_name: '', category: '', calories: 0, season: '', tags: '',
        protein: 5, fiber: 5, vitamins: 5, sugar: 5, saturated_fat: 5, sodium: 5
    })
    showAddDialog.value = true
}

// 提交餐食
const submitMeal = async () => {
    if (!foodForm.food_name) {
        ElMessage.warning('请填写食物名称')
        return
    }
    
    const foodData = {
        food_name: foodForm.food_name,
        category: foodForm.category,
        calories: foodForm.calories,
        season: foodForm.season,
        tags: foodForm.tags,
        protein: foodForm.protein,
        fiber: foodForm.fiber,
        vitamins: foodForm.vitamins,
        sugar: foodForm.sugar,
        saturated_fat: foodForm.saturated_fat,
        sodium: foodForm.sodium,
        is_custom: true  // 自定义食物
    }
    
    // 如果是从数据库选择的，标记为不是自定义
    if (selectedFoodId.value) {
        foodData.is_custom = false
        foodData.food_id = selectedFoodId.value
    }
    
    const res = await api.post('/checkin', {
        user_id: userData.id,
        meal_date: selectedDate.value,
        meal_type: currentMealType.value,
        food_data: foodData
    })
    
    if (res.code === 200) {
        ElMessage.success('添加成功')
        showAddDialog.value = false
        loadMeals()
    } else {
        ElMessage.error(res.message)
    }
}

// 删除餐食
const deleteMeal = async (mealId) => {
    ElMessageBox.confirm('确定删除这条记录吗？', '提示', { type: 'warning' }).then(async () => {
        const res = await api.delete(`/checkin/${mealId}`)
        if (res.code === 200) {
            ElMessage.success('删除成功')
            loadMeals()
        } else {
            ElMessage.error(res.message)
        }
    }).catch(() => {})
}

onMounted(() => {
    loadMeals()
})
</script>

<style scoped>
.checkin-container {
    max-width: 1200px;
    margin: 0 auto;
}

.date-selector {
    margin-bottom: 20px;
    text-align: center;
}

.meal-card {
    height: 100%;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.meal-list {
    min-height: 200px;
}

.meal-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.meal-item .calories {
    color: #e67e22;
    font-size: 12px;
}

.delete-icon {
    cursor: pointer;
    color: #f56c6c;
}

.empty {
    text-align: center;
    color: #999;
    padding: 20px;
}

.custom-form {
    margin-top: 15px;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 8px;
}
</style>