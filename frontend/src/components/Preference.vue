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
                <el-scrollbar max-height="400px">
                    <div v-for="(group, category) in tagGroups" :key="category" class="tag-group">
                        <div class="group-title" :style="{ color: group.color, borderLeftColor: group.color }">
                            {{ category }}
                        </div>
                        <div class="tags-list">
                            <el-tag
                                v-for="tag in group.tags"
                                :key="tag"
                                :type="selectedTags.includes(tag) ? 'primary' : 'info'"
                                effect="plain"
                                @click="toggleTag(tag)"
                                class="tag-item"
                                :style="getTagStyle(tag)"
                            >
                                {{ tag }}
                            </el-tag>
                        </div>
                    </div>
                </el-scrollbar>
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

// 按类别组织的标签（100个，包含原有的10个）
const tagGroups = ref({
    '🌶️ 口味': {
        color: '#e74c3c',
        tags: ['吃辣', '不吃辣', '麻辣', '酸味', '甜味', '咸鲜', '清淡', '浓郁', '清爽', '蒜香', '葱香', '酱香', '烟熏', '烧烤', '卤味', '原味']
    },
    '🥩 食材': {
        color: '#e67e22',
        tags: ['鸡肉', '猪肉', '牛肉', '羊肉', '鱼肉', '虾蟹', '海鲜', '贝类', '蛋类', '豆制品', '菌菇', '根茎类', '叶菜类', '瓜果类', '豆类', '谷物', '坚果', '乳制品', '内脏类', '加工肉制品']
    },
    '🍲 菜系': {
        color: '#9b59b6',
        tags: ['川菜', '粤菜', '鲁菜', '苏菜', '浙菜', '闽菜', '湘菜', '徽菜', '东北菜', '西北菜', '云南菜', '家常菜']
    },
    '🍳 烹饪': {
        color: '#3498db',
        tags: ['炒菜', '蒸菜', '煮菜', '炖菜', '烤制', '煎炸', '凉拌', '红烧', '清汤', '浓汤']
    },
    '💪 健康': {
        color: '#2ecc71',
        tags: ['高蛋白', '低脂', '低碳水', '高纤维', '高钙', '低卡', '高维生素', '均衡营养', '护肝', '养胃', '补血', '增强免疫', '抗氧化', '助消化', '减脂增肌', '少油', '少盐', '少糖']
    },
    '📅 习惯': {
        color: '#1abc9c',
        tags: ['多蔬菜', '多水果', '多喝水', '少食多餐', '规律三餐', '轻断食', '素食主义', '蛋奶素', '严格素食', '快速烹饪']
    },
    '🚫 忌口': {
        color: '#e74c3c',
        tags: ['不吃海鲜', '不吃猪肉', '不吃牛肉', '不吃羊肉', '不吃内脏', '不吃豆制品', '不吃菌菇', '不吃油炸', '不吃甜食']
    },
    '✨ 其他': {
        color: '#f39c12',
        tags: ['廉价食材', '进口食材', '本地食材', '应季食材', '有机食材']
    }
})

const userData = JSON.parse(localStorage.getItem('user') || '{}')

const getTagStyle = (tag) => {
    const len = tag.length
    let fontSize = '12px'
    if (len <= 2) fontSize = '14px'
    else if (len <= 4) fontSize = '13px'
    return { fontSize }
}

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
    if (customTag.value) {
        let exists = false
        for (const group of Object.values(tagGroups.value)) {
            if (group.tags.includes(customTag.value)) {
                exists = true
                break
            }
        }
        if (!exists && !selectedTags.value.includes(customTag.value)) {
            tagGroups.value['✨ 其他'].tags.push(customTag.value)
            selectedTags.value.push(customTag.value)
            customTag.value = ''
            ElMessage.success('自定义标签已添加')
        } else {
            ElMessage.warning('标签已存在')
        }
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
    max-width: 900px;
    margin: 0 auto;
}

.section {
    margin-bottom: 30px;
}

.section h3 {
    margin-bottom: 15px;
    color: #333;
}

.tag-group {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}

.group-title {
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 12px;
    padding-left: 8px;
    border-left: 3px solid;
}

.tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tag-item {
    cursor: pointer;
    transition: all 0.2s ease;
}

.tag-item:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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