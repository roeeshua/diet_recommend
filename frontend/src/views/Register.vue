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
        <el-dialog v-model="showPreference" title="选择你的饮食偏好" width="600px" :close-on-click-modal="false">
            <div class="preference-tags">
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
                
                <el-input
                    v-model="customTag"
                    placeholder="自定义偏好"
                    style="width: 120px; margin: 5px"
                    size="small"
                />
                <el-button size="small" @click="addCustomTag">添加</el-button>
            </div>
            
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

// 预设偏好标签
const allTags = ref(['吃辣', '不吃辣', '素食', '海鲜控', '健身增肌', '减脂', '低卡', '高蛋白', '甜食', '清淡'])
const selectedTags = ref([])
const customTag = ref('')

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
    if (customTag.value && !allTags.value.includes(customTag.value)) {
        allTags.value.push(customTag.value)
        selectedTags.value.push(customTag.value)
        customTag.value = ''
    }
}

const savePreferences = async () => {
    if (!newUserId) {
        ElMessage.error('用户ID丢失，请重新注册')
        return
    }
    
    // 后端是 PUT 方法，不是 POST
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
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.tag-item {
    cursor: pointer;
}
</style>