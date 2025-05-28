<template>
  <el-breadcrumb>
    <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
    <el-breadcrumb-item>应用管理</el-breadcrumb-item>
  </el-breadcrumb>

  <div class="toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        功能菜单
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="add">添加应用</el-dropdown-item>
          <el-dropdown-item @click="removeBatch">批量删除</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>

  <el-table :data="data.list" ref="list" border stripe>
    <el-table-column type="selection" width="38" />
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="token" label="Token" show-overflow-tooltip />
    <el-table-column label="操作">
      <template #default="scope">
        <el-button link type="success" size="small" @click="update(scope.row.id)">编辑</el-button>
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

  <el-dialog
    v-model="data.showEditDialog"
    width="500"
    :title="data.editType == 'add' ? '添加应用' : '编辑应用'">
    <el-form label-width="auto">
      <el-form-item label="名称">
        <el-input v-model="data.app.name" placeholder="请输入名称" />
      </el-form-item>
      <el-form-item label="token">
        <el-input v-model="data.app.token" placeholder="请输入token" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="data.showEditDialog = false">取消</el-button>
      <el-button type="primary" @click="editOK">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
  import { onMounted, reactive, useTemplateRef } from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import http from '../../utils/http'

  const data = reactive({
    list: [],
    tableRef: useTemplateRef('list'),
    showEditDialog: false,
    editType: 'add',
    app: {
      name: '',
      token: '',
    },
    pager: {
      page: 1,
      count: 0,
    },
  })

  const getList = async (page = 1) => {
    const res = await http.post(`/app/list?page=${page}&size=10`)
    data.list = res.data.data.items
    data.pager.page = res.data.data.page
    data.pager.count = res.data.data.pages
  }

  const pageChange = async page => {
    getList(page)
  }

  onMounted(() => {
    getList()
  })

  const add = () => {
    data.showEditDialog = true
    data.editType = 'add'
    data.app = {
      name: '',
      token: '',
    }
  }

  const update = async id => {
    data.showEditDialog = true
    data.editType = 'update'
    const res = await http.post('/app/get', { id })
    data.app = res.data.data
  }

  const remove = async id => {
    const res = await http.post('/app/remove', { id })
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
      const res = await http.post('/app/remove_batch', { ids })
      if (res.data.success) {
        ElMessage.success(res.data.message)
        getList()
      }
    })
  }

  const editOK = async () => {
    if (data.editType === 'add') {
      const res = await http.post('/app/add', data.app)
    } else {
      const res = await http.post('/app/update', data.app)
    }
    ElMessage.success('保存成功')
    data.showEditDialog = false
    getList()
  }
</script>
