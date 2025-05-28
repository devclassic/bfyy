<template>
  <el-card class="login-box">
    <template #header>登录</template>
    <div>
      <el-form label-width="auto">
        <el-form-item label="语音" class="form-item">
          <el-input v-model="form.voice" placeholder="请输入语音识别服务地址" />
        </el-form-item>
        <el-form-item label="账户" class="form-item">
          <el-input v-model="form.account" placeholder="请输入账户" />
        </el-form-item>
        <el-form-item label="密码" class="form-item">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <el-button type="primary" class="login-btn" @click="login">登录</el-button>
    </template>
  </el-card>
</template>

<script setup>
  import { reactive, onMounted, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import http from '../utils/http'

  const router = useRouter()

  const form = reactive({
    voice: '',
    account: '',
    password: '',
  })

  const login = async () => {
    const res = await http.post('/client/login', form)
    if (res.data.success) {
      const apps = res.data.data.apps.split(',')
      if (apps.length > 0) {
        localStorage.setItem('app_id', apps[0])
        localStorage.setItem('token', res.data.data.token)
        localStorage.setItem('account_id', res.data.data.id)
        localStorage.setItem('wsurl', form.voice)
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.warning('当前账户未绑定应用')
      }
    } else {
      ElMessage.error(res.data.message)
    }
  }

  const enter = e => {
    if (e.key === 'Enter') {
      login()
    }
  }

  onMounted(() => {
    form.voice = localStorage.getItem('wsurl') || ''
    addEventListener('keydown', enter)
  })

  onUnmounted(() => {
    removeEventListener('keydown', enter)
  })
</script>

<style scoped>
  .login-box {
    width: 500px;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  .form-item:last-child {
    margin-bottom: 0px;
  }

  .login-btn {
    width: 100%;
  }
</style>
