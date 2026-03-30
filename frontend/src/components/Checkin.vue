<template>
    <div class="checkin-container">
        <h2>饮食打卡</h2>
        
        <el-calendar v-model="currentDate">
            <template #date-cell="{ data }">
                <div class="calendar-day" :class="{ 'has-checkin': hasCheckin(data.day) }">
                    {{ data.day.split('-')[2] }}
                    <span v-if="hasCheckin(data.day)" class="checkin-mark">✓</span>
                </div>
            </template>
        </el-calendar>
        
        <el-dialog v-model="showDialog" :title="`打卡 - ${selectedDate}`">
            <el-form>
                <el-form-item label="今日吃的食物">
                    <el-select v-model="selectedFoods" multiple filterable placeholder="选择食物">
                        <el-option v-for="food in foods" :key="food.id" :label="food.name" :value="food.id" />
                    </el-select>
                </el-form-item>
                <el-form-item label="备注">
                    <el-input v-model="notes" type="textarea" placeholder="可选" />
                </el-form-item>
            </el-form>
            
            <template #footer>
                <el-button @click="showDialog = false">取消</el-button>
                <el-button type="primary" @click="submitCheckin">提交打卡</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const currentDate = ref(new Date())
const showDialog = ref(false)
const selectedDate = ref('')
const selectedFoods = ref([])
const notes = ref('')
const checkins = ref({})
const foods = ref([])

const userData = JSON.parse(localStorage.getItem('user') || '{}')

const hasCheckin = (date) => {
    return checkins.value[date] === true
}

const loadCheckins = async () => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth() + 1
    const res = await api.get(`/checkin/${userData.id}?month=${year}-${month}`)
    if (res.code === 200) {
        const map = {}
        res.data.forEach(item => {
            map[item.date] = true
        })
        checkins.value = map
    }
}

const loadFoods = async () => {
    const res = await api.get('/foods')
    if (res.code === 200) {
        foods.value = res.data
    }
}

const submitCheckin = async () => {
    const res = await api.post('/checkin', {
        user_id: userData.id,
        date: selectedDate.value,
        food_ids: selectedFoods.value,
        notes: notes.value
    })
    
    if (res.code === 200) {
        ElMessage.success('打卡成功')
        showDialog.value = false
        selectedFoods.value = []
        notes.value = ''
        loadCheckins()
    } else {
        ElMessage.error(res.message)
    }
}

onMounted(() => {
    loadCheckins()
    loadFoods()
})
</script>

<style scoped>
.checkin-container {
    max-width: 800px;
    margin: 0 auto;
}

.calendar-day {
    position: relative;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.has-checkin {
    background-color: #d4edda;
    border-radius: 50%;
}

.checkin-mark {
    position: absolute;
    bottom: 2px;
    right: 2px;
    color: green;
    font-size: 12px;
}
</style>