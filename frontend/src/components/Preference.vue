<template>
    <div class="preference-container">
        <h2>饮食偏好设置</h2>
        
        <div class="preference-tags">
            <div class="section">
                <h3>我的偏好</h3>
                <div class="tags-list">
                    <el-tag
                        v-for="tag in selectedTags"
                        :key="tag"
                        closable
                        @close="removeTag(tag)"
                        class="tag-item"
                        type="primary"
                    >
                        {{ tag }}
                    </el-tag>
                    <span v-if="!selectedTags.length" class="empty">暂无偏好，点击下方添加</span>
                </div>
            </div>
            
            <div class="section">
                <h3>推荐偏好</h3>
                <div class="tags-list">
                    <el-tag
                        v-for="tag in allTags"
                        :key="tag"
                        :type="selectedTags.includes(tag) ? 'primary' : 'info'"
                        effect="plain"
                        @click="toggleTag(tag)"
                        class="tag-item"
                    >
                        {{ tag }}
                    </el-tag>
                </div>
            </div>
            
            <div class="section">
                <h3>自定义偏好</h3>
                <div class="custom-input">
                    <el-input v-model="customTag" placeholder="输入新的偏好" style="width: 200px" />
                    <el-button type="primary" @click="addCustomTag">添加</el-button>
                </div>
            </div>
        </div>
        
        <div class="actions">
            <el-button type="primary" @click="savePreferences" :loading="loading">
                保存设置
            </el-button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const loading = ref(false)
const selectedTags = ref([])
const customTag = ref('')
const allTags = ref(['吃辣', '不吃辣', '素食', '海鲜控', '健身增肌', '减脂', '低卡', '高蛋白', '甜食', '清淡'])

const userData = JSON.parse(localStorage.getItem('user') || '{}')

const toggleTag = (tag) => {
    const index = selectedTags.value.indexOf(tag)
    if (index > -1) {
        selectedTags.value.splice(index, 1)
    } else {
        selectedTags.value.push(tag)
    }
}

const removeTag = (tag) => {
    const index = selectedTags.value.indexOf(tag)
    if (index > -1) {
        selectedTags.value.splice(index, 1)
    }
}

const addCustomTag = () => {
    if (customTag.value && !allTags.value.includes(customTag.value)) {
        allTags.value.push(customTag.value)
        selectedTags.value.push(customTag.value)
        customTag.value = ''
    }
}

const loadPreferences = async () => {
    const res = await api.get(`/user/${userData.id}/preferences`)
    if (res.code === 200) {
        selectedTags.value = res.data.map(p => p.value)
    }
}

const savePreferences = async () => {
    loading.value = true
    
    try {
        const res = await api.put(`/user/${userData.id}/preferences/batch`, {
            tags: selectedTags.value
        })
        
        if (res.code === 200) {
            ElMessage.success('偏好设置已保存')
        } else {
            ElMessage.error(res.message)
        }
    } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败，请稍后重试')
    }
    
    loading.value = false
}

onMounted(() => {
    loadPreferences()
})
</script>

<style scoped>
.preference-container {
    max-width: 800px;
    margin: 0 auto;
}

.section {
    margin-bottom: 30px;
}

.section h3 {
    margin-bottom: 15px;
    color: #333;
}

.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.tag-item {
    cursor: pointer;
}

.empty {
    color: #999;
    font-size: 14px;
}

.custom-input {
    display: flex;
    gap: 10px;
    align-items: center;
}

.actions {
    margin-top: 30px;
    text-align: center;
}
</style>