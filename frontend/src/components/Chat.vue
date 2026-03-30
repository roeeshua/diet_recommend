<template>
    <div class="chat-container">
        <h2>AI 饮食助手</h2>
        <p class="desc">我可以根据你的个人信息和饮食偏好，为你解答饮食相关问题</p>
        
        <div class="chat-messages" ref="messagesContainer">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
                <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
                <div class="content">{{ msg.content }}</div>
            </div>
            <div v-if="loading" class="message assistant">
                <div class="avatar">🤖</div>
                <div class="content typing">正在思考中...</div>
            </div>
        </div>
        
        <div class="chat-input">
            <el-input 
                v-model="inputMessage" 
                placeholder="问问我关于饮食的问题，比如：健身应该吃什么？"
                @keyup.enter="sendMessage"
                :disabled="loading"
            />
            <el-button type="primary" @click="sendMessage" :loading="loading">
                发送
            </el-button>
        </div>
        
        <div class="quick-questions">
            <el-tag 
                v-for="q in quickQuestions" 
                :key="q" 
                @click="sendQuickQuestion(q)"
                class="quick-tag"
            >
                {{ q }}
            </el-tag>
        </div>
    </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const loading = ref(false)
const inputMessage = ref('')
const messagesContainer = ref(null)

const userData = JSON.parse(localStorage.getItem('user') || '{}')

const messages = ref([
    { role: 'assistant', content: '你好！我是你的 AI 饮食助手。你可以问我任何关于饮食、营养、健康的问题，我会根据你的个人情况为你解答。' }
])

const quickQuestions = [
    '健身增肌应该吃什么？',
    '减肥期间怎么吃？',
    '推荐一些低卡食材',
    '早餐吃什么比较好？'
]

const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

const sendMessage = async () => {
    if (!inputMessage.value.trim()) return
    
    const userMsg = inputMessage.value
    messages.value.push({ role: 'user', content: userMsg })
    inputMessage.value = ''
    await scrollToBottom()
    
    loading.value = true
    
    // 调用后端 AI 助手接口（需要后端实现）
    try {
        const res = await api.post('/chat', {
            user_id: userData.id,
            message: userMsg
        })
        
        if (res.code === 200) {
            messages.value.push({ role: 'assistant', content: res.data.response })
        } else {
            messages.value.push({ role: 'assistant', content: '抱歉，我现在无法回答，请稍后再试。' })
        }
    } catch (error) {
        messages.value.push({ role: 'assistant', content: '网络错误，请稍后再试。' })
    }
    
    loading.value = false
    await scrollToBottom()
}

const sendQuickQuestion = (question) => {
    inputMessage.value = question
    sendMessage()
}
</script>

<style scoped>
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 120px);
}

.desc {
    color: #666;
    margin-bottom: 15px;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    background: white;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}

.message {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.message.user {
    flex-direction: row-reverse;
}

.message.user .content {
    background: #667eea;
    color: white;
}

.message.assistant .content {
    background: #f0f0f0;
    color: #333;
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.content {
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 18px;
    line-height: 1.5;
}

.typing {
    color: #999;
}

.chat-input {
    display: flex;
    gap: 10px;
}

.quick-questions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 15px;
}

.quick-tag {
    cursor: pointer;
}
</style>