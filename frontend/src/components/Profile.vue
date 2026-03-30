<template>
    <div class="profile-container">
        <h2>个人主页</h2>
        <el-card class="profile-card">
            <el-descriptions :column="2" border>
                <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
                <el-descriptions-item label="年龄">
                    <el-input-number v-model="editForm.age" :min="1" :max="120" size="small" />
                </el-descriptions-item>
                <el-descriptions-item label="性别">
                    <el-radio-group v-model="editForm.gender">
                        <el-radio :label="true">男</el-radio>
                        <el-radio :label="false">女</el-radio>
                    </el-radio-group>
                </el-descriptions-item>
                <el-descriptions-item label="身高(cm)">
                    <el-input-number v-model="editForm.height" :min="50" :max="250" size="small" />
                </el-descriptions-item>
                <el-descriptions-item label="体重(kg)">
                    <el-input-number v-model="editForm.weight" :min="20" :max="300" size="small" />
                </el-descriptions-item>
                <el-descriptions-item label="注册时间">{{ user.created_at || '未知' }}</el-descriptions-item>
            </el-descriptions>
            
            <div class="actions">
                <el-button type="primary" @click="saveProfile">保存修改</el-button>
            </div>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const user = ref({})
const editForm = ref({
    age: null,
    gender: null,
    height: null,
    weight: null
})

const loadUser = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    const res = await api.get(`/user/${userData.id}`)
    if (res.code === 200) {
        user.value = res.data
        editForm.value = {
            age: res.data.age,
            gender: res.data.gender,
            height: res.data.height,
            weight: res.data.weight
        }
    }
}

const saveProfile = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}')
    const res = await api.put(`/user/${userData.id}`, editForm.value)
    if (res.code === 200) {
        ElMessage.success('保存成功')
        localStorage.setItem('user', JSON.stringify(res.data))
        loadUser()
    } else {
        ElMessage.error(res.message)
    }
}

onMounted(() => {
    loadUser()
})
</script>

<style scoped>
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
}

.profile-card {
    margin-top: 20px;
}

.actions {
    margin-top: 20px;
    text-align: center;
}
</style>