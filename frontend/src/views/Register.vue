<template>
    <div class="register-container">
        <div class="register-card">
            <h2>注册账号</h2>
            
            <el-form :model="form" label-position="top">
                <el-form-item label="用户名">
                    <el-input v-model="form.username" placeholder="请输入用户名" />
                </el-form-item>
                
                <el-form-item label="密码">
                    <el-input v-model="form.password" type="password" placeholder="请输入密码" />
                </el-form-item>
                
                <el-form-item label="年龄">
                    <el-input-number v-model="form.age" :min="1" :max="120" />
                </el-form-item>
                
                <el-form-item label="性别">
                    <el-radio-group v-model="form.gender">
                        <el-radio :label="true">男</el-radio>
                        <el-radio :label="false">女</el-radio>
                    </el-radio-group>
                </el-form-item>
                
                <el-form-item label="身高(cm)">
                    <el-input-number v-model="form.height" :min="50" :max="250" />
                </el-form-item>
                
                <el-form-item label="体重(kg)">
                    <el-input-number v-model="form.weight" :min="20" :max="300" />
                </el-form-item>
                
                <el-button type="primary" @click="handleRegister" :loading="loading">
                    注册
                </el-button>
                
                <div class="login-link">
                    已有账号？<el-link type="primary" @click="$router.push('/login')">去登录</el-link>
                </div>
            </el-form>
        </div>
        
        <!-- 偏好选择弹窗（首次注册后显示） -->
        <el-dialog v-model="showPreference" title="选择你的饮食偏好" width="700px" :close-on-click-modal="false">
            <el-scrollbar max-height="400px">
                <div class="preference-tags">
                    <!-- 按类别分组显示 -->
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
                    
                    <!-- 自定义标签 -->
                    <div class="custom-section">
                        <el-input
                            v-model="customTag"
                            placeholder="自定义偏好"
                            style="width: 150px"
                            size="small"
                        />
                        <el-button size="small" type="primary" @click="addCustomTag">添加</el-button>
                    </div>
                </div>
            </el-scrollbar>
            
            <template #footer>
                <el-button @click="skipPreference">跳过</el-button>
                <el-button type="primary" @click="savePreferences">确认</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const showPreference = ref(false)
let newUserId = null

const form = ref({
    username: '',
    password: '',
    age: null,
    gender: null,
    height: null,
    weight: null
})

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

// 获取标签样式
const getTagStyle = (tag) => {
    const len = tag.length
    let fontSize = '12px'
    if (len <= 2) fontSize = '14px'
    else if (len <= 4) fontSize = '13px'
    return { fontSize }
}

const handleRegister = async () => {
    if (!form.value.username || !form.value.password) {
        ElMessage.warning('请填写用户名和密码')
        return
    }
    
    loading.value = true
    try {
        const res = await api.post('/register', {
            username: form.value.username,
            password: form.value.password,
            age: form.value.age,
            gender: form.value.gender,
            height: form.value.height,
            weight: form.value.weight
        })
        
        if (res.code === 200) {
            newUserId = res.data.id
            ElMessage.success('注册成功！请选择你的饮食偏好')
            showPreference.value = true
        } else if (res.code === 400 && res.message === '用户名已存在') {
            ElMessage.error('用户名已被使用，请重新命名')
        } else {
            ElMessage.error(res.message || '注册失败，请稍后重试')
        }
    } catch (error) {
        console.error('注册请求失败:', error)
        ElMessage.error('网络错误，请检查后端服务是否正常运行')
    } finally {
        loading.value = false
    }
}

const toggleTag = (tag) => {
    const index = selectedTags.value.indexOf(tag)
    if (index > -1) {
        selectedTags.value.splice(index, 1)
    } else {
        selectedTags.value.push(tag)
    }
}

const addCustomTag = () => {
    if (customTag.value) {
        // 检查是否已存在
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
        }
    }
}

const savePreferences = async () => {
    if (!newUserId) {
        ElMessage.error('用户ID丢失，请重新注册')
        return
    }
    
    const res = await api.put(`/user/${newUserId}/preferences/batch`, {
        tags: selectedTags.value
    })
    
    if (res.code === 200) {
        showPreference.value = false
        ElMessage.success('偏好设置完成')
        router.push('/login')
    } else {
        ElMessage.error(res.message || '保存失败')
    }
}

const skipPreference = () => {
    showPreference.value = false
    router.push('/login')
}
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
    width: 450px;
    padding: 30px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.register-card h2 {
    text-align: center;
    margin-bottom: 20px;
}

.el-button {
    width: 100%;
}

.login-link {
    text-align: center;
    margin-top: 15px;
}

.preference-tags {
    padding: 10px;
}

.tag-group {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.group-title {
    font-size: 14px;
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

.custom-section {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 15px;
    padding-top: 10px;
}
</style>