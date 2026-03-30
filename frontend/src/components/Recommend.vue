<template>
    <div class="recommend-container">
        <h2>饮食推荐</h2>
        <p class="desc">根据你的饮食偏好，AI 为你推荐以下食材：</p>
        
        <el-button type="primary" @click="loadRecommend" :loading="loading">
            刷新推荐
        </el-button>
        
        <div class="food-grid" v-if="foods.length">
            <el-card v-for="food in foods" :key="food.id" class="food-card">
                <h3>{{ food.name }}</h3>
                <p class="category">{{ food.category }}</p>
                <p class="calories">{{ food.calories }} 卡 / 100g</p>
                <div class="tags">
                    <el-tag v-for="tag in food.tags" :key="tag" size="small">
                        {{ tag }}
                    </el-tag>
                </div>
            </el-card>
        </div>
        
        <el-empty v-else description="暂无推荐，请先设置饮食偏好" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const loading = ref(false)
const foods = ref([])

const loadRecommend = async () => {
    loading.value = true
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    const res = await api.get(`/recommend/${userData.id}`)
    loading.value = false
    if (res.code === 200) {
        foods.value = res.data
    }
}

onMounted(() => {
    loadRecommend()
})
</script>

<style scoped>
.recommend-container {
    max-width: 1000px;
    margin: 0 auto;
}

.desc {
    color: #666;
    margin-bottom: 20px;
}

.food-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.food-card {
    text-align: center;
}

.food-card h3 {
    margin: 0 0 10px 0;
    color: #333;
}

.category {
    color: #667eea;
    font-size: 14px;
    margin: 5px 0;
}

.calories {
    color: #e67e22;
    font-weight: bold;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    margin-top: 10px;
}
</style>