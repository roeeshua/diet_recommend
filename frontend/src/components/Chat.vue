<template>
    <div class="chat-container">
        <div class="chat-header">
            <h2>AI 饮食助手</h2>
            <el-button type="danger" size="small" @click="clearHistory">
                清空会话历史
            </el-button>
            <div class="model-switch">
                <span>🤖 模型选择：</span>
                <el-radio-group v-model="currentModel" @change="switchModel" size="small">
                    <el-radio-button value="ollama">本地 Ollama</el-radio-button>
                    <el-radio-button value="deepseek">外部 API</el-radio-button>
                </el-radio-group>
            </div>
        </div>
        <p class="desc">我可以根据你的个人信息、饮食偏好和历史饮食记录，为你提供个性化的饮食建议</p>
        
        <!-- 上下文配置面板 -->
        <el-card class="context-card">
            <div class="context-header">
                <span>📋 上下文设置</span>
                <el-button type="primary" link @click="showContext = !showContext">
                    {{ showContext ? '收起' : '展开' }}
                </el-button>
            </div>
            
            <div v-show="showContext" class="context-content">
                <el-form label-width="140px">
                    <el-form-item label="读取用户基本信息">
                        <el-switch v-model="includeProfile" active-text="开启" inactive-text="关闭" />
                        <span class="hint">（年龄、性别、身高、体重）</span>
                    </el-form-item>

                    <el-form-item label="读取饮食偏好">
                        <el-switch v-model="includePreference" active-text="开启" inactive-text="关闭" />
                        <span class="hint">（口味偏好、忌口等）</span>
                    </el-form-item>

                    <el-form-item label="读取饮食画像">
                        <el-switch v-model="includeUserProfile" active-text="开启" inactive-text="关闭" />
                        <span class="hint">（基于30天打卡的饮食特征）</span>
                    </el-form-item>
                    
                    <el-form-item label="读取历史饮食记录">
                        <el-switch v-model="includeHistory" active-text="开启" inactive-text="关闭" />
                    </el-form-item>
                    
                    <el-form-item v-if="includeHistory" label="统计周期">
                        <el-date-picker
                            v-model="dateRange"
                            type="daterange"
                            range-separator="至"
                            start-placeholder="开始日期"
                            end-placeholder="结束日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD"
                        />
                    </el-form-item>
                </el-form>
            </div>
        </el-card>
        
        <!-- 聊天区域 -->
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
        
        <!-- 快捷问题 -->
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
        
        <!-- 输入区域 -->
        <div class="chat-input">
            <el-input 
                v-model="inputMessage" 
                placeholder="问问我关于饮食的问题，比如：根据我的情况，我应该怎么调整饮食？"
                @keyup.enter="sendMessage"
                :disabled="loading"
            />
            <el-button type="primary" @click="sendMessage" :loading="loading">
                发送
            </el-button>
        </div>
    </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const loading = ref(false)
const inputMessage = ref('')
const messagesContainer = ref(null)
const showContext = ref(false)
const includeProfile = ref(true)
const includePreference = ref(true)  // 新增：读取饮食偏好
const includeHistory = ref(false)
const dateRange = ref(null)
const includeUserProfile = ref(true)  // 是否包含饮食画像

const currentModel = ref('ollama')

const userData = JSON.parse(localStorage.getItem('user') || '{}')

// 获取当前使用的模型
const getCurrentModel = async () => {
    const res = await api.get('/ai/get_model')
    if (res.code === 200) {
        currentModel.value = res.data.engine
    }
}

// 切换模型
const switchModel = async () => {
    const res = await api.post('/ai/switch_model', { engine: currentModel.value })
    if (res.code === 200) {
        ElMessage.success(res.message)
    } else {
        ElMessage.error(res.message)
        // 切换失败，恢复原值
        currentModel.value = currentModel.value === 'ollama' ? 'deepseek' : 'ollama'
    }
}

onMounted(() => {
    getCurrentModel()
})

const messages = ref([
    { role: 'assistant', content: '你好！我是你的 AI 饮食助手。我可以根据你的个人信息、饮食偏好和历史饮食记录，为你提供个性化的饮食建议。' }
])

const quickQuestions = [
    '根据我的情况，饮食上有什么建议？',
    '我的营养指标哪些需要改善？',
    '推荐一周的健康食谱',
    '我的热量摄入是否合理？',
    '健身增肌应该怎么吃？',
    '哪些营养我需要多补充？'
]

const scrollToBottom = async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

const sendMessage = async () => {
    console.log(`当前使用模型: ${currentModel.value}`)
    if (!inputMessage.value.trim()) return
    
    const userMsg = inputMessage.value
    messages.value.push({ role: 'user', content: userMsg })
    inputMessage.value = ''
    await scrollToBottom()
    
    loading.value = true
    
    try {
        const requestBody = {
            user_id: userData.id,
            message: userMsg,
            include_profile: includeProfile.value,
            include_preference: includePreference.value,  
            include_user_profile: includeUserProfile.value,
            include_history: includeHistory.value
        }
        
        if (includeHistory.value && dateRange.value) {
            requestBody.start_date = dateRange.value[0]
            requestBody.end_date = dateRange.value[1]
        }
        
        const res = await api.post('/ai/chat', requestBody)
        
        if (res.code === 200) {
            messages.value.push({ role: 'assistant', content: res.data.response })
        } else {
            messages.value.push({ role: 'assistant', content: res.message || '抱歉，我现在无法回答，请稍后再试。' })
        }
    } catch (error) {
        console.error('AI 对话失败:', error)
        messages.value.push({ role: 'assistant', content: '网络错误，请稍后再试。' })
    }
    
    loading.value = false
    await scrollToBottom()
}

const sendQuickQuestion = (question) => {
    inputMessage.value = question
    sendMessage()
}

// 清空会话历史
const clearHistory = () => {
    messages.value = [
        { role: 'assistant', content: '你好！我是你的 AI 饮食助手。会话历史已清空，有什么我可以帮你的吗？' }
    ]
    ElMessage.success('会话历史已清空')
}
</script>

<style scoped>
.chat-container {
    max-width: 1000px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 120px);
}

.desc {
    color: #666;
    margin-bottom: 15px;
}

.context-card {
    margin-bottom: 15px;
    flex-shrink: 0;
}

.context-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}

.context-content {
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #eee;
}

.hint {
    margin-left: 10px;
    color: #999;
    font-size: 12px;
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
    white-space: pre-wrap;
}

.typing {
    color: #999;
}

.chat-input {
    display: flex;
    gap: 10px;
    flex-shrink: 0;
}

.quick-questions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
    flex-shrink: 0;
}

.quick-tag {
    cursor: pointer;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.model-switch {
    display: flex;
    align-items: center;
    gap: 10px;
}

</style>