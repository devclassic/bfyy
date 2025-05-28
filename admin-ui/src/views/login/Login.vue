<template>
  <el-card class="login-box">
    <template #header>智能应用管理系统</template>
    <div>
      <el-form label-width="auto">
        <el-form-item label="账户" class="form-item">
          <el-input v-model="form.username" placeholder="请输入账户" />
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
  import http from '../../utils/http'

  const router = useRouter()

  const form = reactive({
    username: '',
    password: '',
  })

  const login = async () => {
    try {
      const res = await http.post('/auth/login', form)
      if (res.data.success) {
        ElMessage.success('登录成功')
        sessionStorage.setItem('user', form.username)
        sessionStorage.setItem('token', res.data.token)
        router.push('/')
      } else {
        ElMessage.error(res.data.message)
      }
    } catch (e) {
      ElMessage.error(e)
    }
  }

  const enter = e => {
    if (e.key === 'Enter') {
      login()
    }
  }

  onMounted(() => {
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
