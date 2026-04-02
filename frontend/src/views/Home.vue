<template>
    <el-container class="home-container">
        <!-- 左侧导航栏 -->
        <el-aside width="300px" class="sidebar">
            <div class="logo">
                <h2>🍽️ 饮食助手</h2>
            </div>
            
            <el-menu
                :default-active="activeMenu"
                class="sidebar-menu"
                @select="handleMenuSelect"
            >
                <el-menu-item index="profile">
                    <el-icon><User /></el-icon>
                    <span>个人主页</span>
                </el-menu-item>
                <el-menu-item index="plan">
                    <el-icon><Calendar /></el-icon>
                    <span>饮食计划</span>
                </el-menu-item>
                <el-menu-item index="saved">
                    <el-icon><Star /></el-icon>
                    <span>我的计划库</span>
                </el-menu-item>
                <el-menu-item index="recommend">
                    <el-icon><Star /></el-icon>
                    <span>饮食推荐</span>
                </el-menu-item>
                <el-menu-item index="chat">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>AI 助手</span>
                </el-menu-item>
                <el-menu-item index="checkin">
                    <el-icon><Checked /></el-icon>
                    <span>饮食打卡</span>
                </el-menu-item>
                <el-menu-item index="statistics">
                    <el-icon><DataLine /></el-icon>
                    <span>营养统计</span>
                </el-menu-item>
                <el-menu-item index="preference">
                    <el-icon><Setting /></el-icon>
                    <span>偏好设置</span>
                </el-menu-item>
            </el-menu>
            
            <div class="logout-btn">
                <el-button type="danger" @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                </el-button>
            </div>
        </el-aside>
        
        <!-- 右侧内容区 -->
        <el-main class="main-content">
            <keep-alive include="Chat">
                <component :is="currentComponent" />
            </keep-alive>
        </el-main>
    </el-container>
</template>

<script setup>
import { ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Profile from '../components/Profile.vue'
import Plan from '../components/Plan.vue'
import SavedPlans from '../components/SavedPlans.vue'
import Recommend from '../components/Recommend.vue'
import Chat from '../components/Chat.vue'
import Checkin from '../components/Checkin.vue'
import Statistics from '../components/Statistics.vue'
import Preference from '../components/Preference.vue'

const router = useRouter()
const activeMenu = ref('profile')

const componentMap = {
    profile: Profile,
    plan: Plan,
    saved: SavedPlans,
    recommend: Recommend,
    chat: Chat,
    checkin: Checkin,
    statistics: Statistics,
    preference: Preference
}

const currentComponent = shallowRef(Profile)

const handleMenuSelect = (index) => {
    activeMenu.value = index
    currentComponent.value = componentMap[index]
}

const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/login')
}
</script>

<style scoped>
.home-container {
    height: 100vh;
    min-width: 1200px;
}

.sidebar {
    background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
    color: white;
    display: flex;
    flex-direction: column;
}

.logo {
    padding: 20px;
    text-align: center;
    border-bottom: 1px solid #4a5568;
}

.logo h2 {
    color: #fbbf24;
    margin: 0;
    font-size: 24px;
}

.sidebar-menu {
    flex: 1;
    background: transparent;
    border-right: none;
}

.sidebar-menu .el-menu-item {
    color: #e2e8f0;
    height: 56px;
    font-size: 16px;
}

.sidebar-menu .el-menu-item:hover {
    background-color: #4a5568;
}

.sidebar-menu .el-menu-item.is-active {
    background-color: #667eea;
    color: white;
}

.logout-btn {
    padding: 20px;
    border-top: 1px solid #4a5568;
}

.logout-btn .el-button {
    width: 100%;
}

.main-content {
    background: #f5f7fa;
    padding: 30px;
    overflow-y: auto;
}
</style>