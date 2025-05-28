<template>
  <div class="box">
    <div class="toolbar">
      <div>
        <el-input
          v-model="data.input"
          type="textarea"
          :rows="3"
          placeholder="请输入问题"
          class="input" />
      </div>
      <div>
        <div>
          <el-button type="info" :disabled="data.recordDisabled" @click="handleRecord">
            {{ data.recordBtnText }}
          </el-button>
          <el-button type="primary" :disabled="data.submitDisabled" @click="submit">
            {{ data.submitBtnText }}
          </el-button>
        </div>
        <div style="margin-top: 8px">
          <el-button type="success" :disabled="data.newDisabled" @click="newChat">
            新的对话
          </el-button>
          <el-button type="danger" @click="logout">退出登录</el-button>
        </div>
      </div>
    </div>
    <div ref="content" class="content">
      <div v-for="item in data.qas" :key="item.id" class="qa-box">
        <div class="question">{{ item.question }}</div>
        <div class="answer">
          <div v-if="item.answer" v-html="item.answer"></div>
          <div v-else class="answer-loading">处理中...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, useTemplateRef, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessageBox, ElMessage } from 'element-plus'
  import { v4 as uuidv4 } from 'uuid'
  import markdown from 'markdown-it'
  import Asr from '../utils/asr'
  import http from '../utils/http'

  const router = useRouter()

  const md = markdown()

  const data = reactive({
    input: '',
    recordDisabled: true,
    submitDisabled: false,
    newDisabled: true,
    isRecording: false,
    recordBtnText: '开始收音',
    submitBtnText: '提交问题',
    qas: [],
    chatId: uuidv4(),
    contentRef: useTemplateRef('content'),
  })

  const newChat = () => {
    data.chatId = uuidv4()
    data.qas = []
    data.input = ''
  }

  const submit = async () => {
    if (!data.input) {
      ElMessageBox.alert('请输入有效问题', '提示')
      return
    }
    data.recordDisabled = true
    data.newDisabled = true
    data.submitDisabled = true
    data.submitBtnText = '处理中...'
    let qa = {
      id: uuidv4(),
      question: data.input,
      answer: '',
    }
    data.qas.push(qa)
    data.input = ''
    nextTick(() => {
      data.contentRef.scroll({
        top: data.contentRef.scrollHeight,
        behavior: 'smooth',
      })
    })
    const res = await http.post('/client/chat', {
      app_id: localStorage.getItem('app_id'),
      account_id: localStorage.getItem('account_id'),
      chatid: data.chatId,
      question: qa.question,
    })
    qa.answer = md.render(res.data.data.replace(/<think>[\s\S]*?<\/think>/g, ''))
    data.qas = [...data.qas]
    data.recordDisabled = false
    data.newDisabled = false
    data.submitDisabled = false
    data.submitBtnText = '提交问题'
    nextTick(() => {
      data.contentRef.scroll({
        top: data.contentRef.scrollHeight,
        behavior: 'smooth',
      })
    })
  }

  const logout = async () => {
    try {
      await ElMessageBox.confirm('确定退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
      localStorage.removeItem('token')
      router.push('/login')
    } catch {}
  }

  const asr = new Asr()

  asr.ontext = text => {
    data.input = text
  }

  asr.onopen = () => {
    ElMessage.success('连接语音识别服务成功')
  }

  asr.onerror = e => {
    ElMessageBox.alert('连接语音识别服务错误', '提示')
  }

  asr.onclose = () => {
    data.recordDisabled = true
    data.newDisabled = true
  }

  asr.getPermission().then(
    () => {
      data.recordDisabled = false
      data.submitDisabled = false
      data.newDisabled = false
    },
    e => {
      data.recordDisabled = true
      console.log('获取录音权限失败', e)
      ElMessageBox.alert('获取录音权限失败，请检查浏览器设置或语音服务配置', '提示')
    },
  )

  const handleRecord = () => {
    if (!data.isRecording) {
      data.isRecording = true
      data.recordBtnText = '停止收音'
      asr.start(
        () => {
          data.submitDisabled = true
          data.newDisabled = true
        },
        () => {
          console.log('开启收音失败', e)
          ElMessageBox.alert('开启收音失败，请检查浏览器设置或语音服务配置', '提示')
        },
      )
    } else {
      data.isRecording = false
      data.recordBtnText = '开始收音'
      asr.stop(() => {
        data.submitDisabled = false
        data.newDisabled = false
      })
    }
  }
</script>

<style scoped>
  .box {
    width: 800px;
    margin: 0 auto;
  }

  .toolbar {
    margin-top: 10px;
    display: flex;
  }

  .input {
    width: 600px;
    margin-right: 12px;
  }

  .content {
    border: 1px solid #ddd;
    margin-top: 10px;
    padding: 10px;
    height: calc(100vh - 105px);
    overflow: auto;
  }

  .qa-box {
    margin-bottom: 20px;
  }

  .question {
    color: red;
    margin-bottom: 5px;
  }

  .answer {
    color: blue;
  }

  .answer-loading {
    color: #ccc;
  }
</style>
