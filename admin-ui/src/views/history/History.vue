<template>
  <el-breadcrumb>
    <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
    <el-breadcrumb-item>数据管理</el-breadcrumb-item>
  </el-breadcrumb>

  <div class="toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        功能菜单
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="exportdata">导出数据</el-dropdown-item>
          <el-dropdown-item @click="removeBatch">批量删除</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>

  <el-table :data="data.list" ref="list" border stripe>
    <el-table-column type="selection" width="38" />
    <el-table-column prop="account.name" label="账户" />
    <el-table-column prop="app.name" label="应用" />
    <el-table-column prop="question_time" label="提问时间" />
    <el-table-column prop="question" label="问题" show-overflow-tooltip />
    <el-table-column prop="answer_time" label="回答时间" />
    <el-table-column prop="answer" label="回答" show-overflow-tooltip />
    <el-table-column label="操作">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="showInfo(scope.row.id)">查看</el-button>
        <el-popconfirm
          title="确认删除？"
          confirm-button-text="确定"
          cancel-button-text="取消"
          @confirm="remove(scope.row.id)">
          <template #reference>
            <el-button link type="danger" size="small">删除</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-table-column>
  </el-table>

  <div class="pager">
    <el-pagination
      background
      layout="prev, pager, next"
      :current-page="data.pager.page"
      :page-count="data.pager.count"
      @current-change="pageChange" />
  </div>

  <el-dialog v-model="data.showInfoDialog" width="500" title="查看数据">
    <div style="color: red">问题 {{ data.history.question_time }}：</div>
    <div style="margin-bottom: 10px">{{ data.history.question }}</div>
    <div style="color: blue">回答 {{ data.history.answer_time }}：</div>
    <div v-html="data.history.answer"></div>
    <template #footer>
      <el-button @click="data.showInfoDialog = false">取消</el-button>
      <el-button type="primary" @click="data.showInfoDialog = false">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
  import { onMounted, reactive, useTemplateRef, computed, nextTick } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { formatInTimeZone } from 'date-fns-tz'
  import markdown from 'markdown-it'
  import http from '../../utils/http'

  const md = markdown()

  const data = reactive({
    list: [],
    tableRef: useTemplateRef('list'),
    showInfoDialog: false,
    history: {},
    pager: {
      page: 1,
      count: 0,
    },
  })

  const exportdata = async () => {
    const a = document.createElement('a')
    a.href = import.meta.env.VITE_API_BASE_URL + '/history/export'
    a.download = '问答历史数据.xlsx'
    a.click()
  }

  const getList = async (page = 1) => {
    const res = await http.post(`/history/list?page=${page}&size=10`)
    data.list = res.data.data.items.map(item => {
      item.question_time = formatInTimeZone(
        new Date(item.question_time),
        'UTC',
        'yyyy-MM-dd HH:mm:ss',
      )
      item.answer_time = formatInTimeZone(new Date(item.answer_time), 'UTC', 'yyyy-MM-dd HH:mm:ss')
      return item
    })
    data.pager.page = res.data.data.page
    data.pager.count = res.data.data.pages
  }

  const pageChange = async page => {
    getList(page)
  }

  onMounted(() => {
    getList()
  })

  const remove = async id => {
    const res = await http.post('/history/remove', { id })
    if (res.data.success) {
      ElMessage.success(res.data.message)
      getList()
    }
  }

  const removeBatch = async () => {
    ElMessageBox.confirm('确认删除选中的行？', '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(async () => {
      const rows = data.tableRef.getSelectionRows()
      if (rows.length === 0) {
        ElMessage.warning('请选择要删除的行')
        return
      }
      const ids = rows.map(row => row.id)
      const res = await http.post('/history/remove_batch', { ids })
      if (res.data.success) {
        ElMessage.success(res.data.message)
        getList()
      }
    })
  }

  const showInfo = async id => {
    data.history = {}
    data.showInfoDialog = true
    const res = await http.post('/history/get', { id })
    data.history = res.data.data
    data.history.question_time = formatInTimeZone(
      new Date(data.history.question_time),
      'UTC',
      'yyyy-MM-dd HH:mm:ss',
    )
    data.history.answer_time = formatInTimeZone(
      new Date(data.history.answer_time),
      'UTC',
      'yyyy-MM-dd HH:mm:ss',
    )
    data.history.answer = md.render(data.history.answer)
  }
</script>
