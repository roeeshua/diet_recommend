<template>
    <div class="login-container">
        <div class="login-card">
            <h2>饮食推荐系统</h2>
            <p class="subtitle">基于大语言模型的智能饮食助手</p>
            
            <el-form :model="form" @submit.prevent="handleLogin">
                <el-form-item>
                    <el-input 
                        v-model="form.username" 
                        placeholder="用户名"
                        prefix-icon="User"
                        size="large"
                    />
                </el-form-item>
                
                <el-form-item>
                    <el-input 
                        v-model="form.password" 
                        :type="showPassword ? 'text' : 'password'"
                        placeholder="密码"
                        prefix-icon="Lock"
                        size="large"
                    >
                        <template #suffix>
                            <el-icon @click="showPassword = !showPassword" style="cursor: pointer">
                                <View v-if="showPassword" />
                                <Hide v-else />
                            </el-icon>
                        </template>
                    </el-input>
                </el-form-item>
                
                <el-button type="primary" size="large" @click="handleLogin" :loading="loading">
                    登录
                </el-button>
                
                <div class="register-link">
                    还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
                </div>
            </el-form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const showPassword = ref(false)

const form = ref({
    username: '',
    password: ''
})

const handleLogin = async () => {
    if (!form.value.username || !form.value.password) {
        ElMessage.warning('请填写用户名和密码')
        return
    }
    
    loading.value = true
    const res = await api.post('/login', form.value)
    loading.value = false
    
    if (res.code === 200) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        ElMessage.success('登录成功')
        router.push('/home')
    } else {
        ElMessage.error(res.message)
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.login-card h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 10px;
}

.subtitle {
    color: #666;
    margin-bottom: 30px;
}

.el-button {
    width: 100%;
    margin-top: 10px;
}

.register-link {
    margin-top: 20px;
    color: #666;
}
</style>