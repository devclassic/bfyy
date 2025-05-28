<template>
  <el-breadcrumb>
    <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
    <el-breadcrumb-item>知识库管理</el-breadcrumb-item>
  </el-breadcrumb>

  <div class="toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        功能菜单
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-if="isroot" @click="showSettings">设置</el-dropdown-item>
          <el-dropdown-item disabled>其他功能</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>

  <el-table :data="data.list" border stripe>
    <el-table-column prop="name" label="名称" />
    <el-table-column label="操作">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="showKnowledge(scope.row)">
          查看
        </el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="data.showSettings" width="500" title="知识库设置">
    <el-form label-width="auto">
      <el-form-item label="知识库">
        <el-input v-model="data.settings.knowledge_base" placeholder="请输入知识库ID" />
      </el-form-item>
      <el-form-item label="Dify接口">
        <el-input v-model="data.settings.api_base" placeholder="请输入Dify接口" />
      </el-form-item>
      <el-form-item label="Dify密钥">
        <el-input v-model="data.settings.api_base_token" placeholder="请输入Dify密钥" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="data.showSettings = false">取消</el-button>
      <el-button type="primary" @click="settingsOK">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog
    v-model="data.showKnowledge"
    width="500"
    :title="data.knowledgeName"
    @close="closeKnowledge">
    <div class="knowledge-toolbar">
      <el-dropdown trigger="click">
        <el-button type="primary">
          知识库
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="showUpload">上传文件</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <el-table v-loading="data.showCollectionsLoading" :data="data.collections" border stripe>
      <el-table-column prop="name" label="名称" show-overflow-tooltip />
      <el-table-column label="状态" width="90">
        <template #default="scope">
          <el-tag :type="scope.row.trainingAmount > 0 ? 'info' : 'success'">
            {{ scope.row.indexing_status === 'completed' ? '就绪' : '处理中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-popconfirm
            title="确认删除？"
            confirm-button-text="确定"
            cancel-button-text="取消"
            @confirm="removeCollection(scope.row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-button @click="closeKnowledge">取消</el-button>
      <el-button type="primary" @click="closeKnowledge">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="data.showUpload" width="500" title="上传文件">
    <!-- <el-form label-width="auto">
      <el-form-item label="处理模式" style="margin-bottom: 10px">
        <el-select v-model="data.trainingType" placeholder="请选择处理模式">
          <el-option
            v-for="item in data.trainingTypeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value" />
        </el-select>
      </el-form-item>
    </el-form> -->
    <el-upload
      ref="upload"
      drag
      multiple
      :headers="{ token }"
      :action="`${api_base_url}/knowledge/upload`"
      :on-success="uploadSuccess">
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽 或
        <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">请上传常见文档类型（txt, pdf, docx, md, txt, html, csv...等）小于10M</div>
      </template>
    </el-upload>
    <template #footer>
      <el-button @click="data.showUpload = false">取消</el-button>
      <el-button type="primary" :loading="data.showUploadBtnLoding" @click="uploadOK">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
  import { onMounted, reactive, useTemplateRef } from 'vue'
  import { ElMessage } from 'element-plus'
  import http from '../../utils/http'

  const isroot = sessionStorage.getItem('user') === 'root'

  const api_base_url = import.meta.env.VITE_API_BASE_URL
  const token = sessionStorage.getItem('token')

  const data = reactive({
    list: [],
    collections: [],
    showSettings: false,
    knowledgeName: '',
    knowledgeId: '',
    showKnowledge: false,
    trainingType: '',
    trainingTypeOptions: [
      {
        label: '分段',
        value: 'chunk',
      },
      {
        label: '问答',
        value: 'qa',
      },
    ],
    showUpload: false,
    showCollectionsLoading: false,
    showUploadBtnLoding: false,
    uploadRef: useTemplateRef('upload'),
    files: [],
    settings: {
      knowledge_base: '',
      api_base: '',
      api_base_token: '',
    },
  })

  const showUpload = async () => {
    data.files = []
    data.showUpload = true
    data.trainingType = ''
  }

  const uploadOK = async () => {
    try {
      data.showUploadBtnLoding = true
      const res = await http.post('/knowledge/add_file_collection', {
        files: data.files,
        dataset_id: data.knowledgeId,
      })
      if (res.data.success) {
        data.files = []
        data.uploadRef.clearFiles()
        getCollections()
        data.showUpload = false
      }
    } catch (e) {
      ElMessage.error(e)
    } finally {
      data.showUploadBtnLoding = false
    }
  }

  const showSettings = async () => {
    data.showSettings = true
    const res = await http.post('/knowledge/get_settings')
    data.settings = res.data.data
  }

  const removeCollection = async id => {
    data.showCollectionsLoading = true
    const res = await http.post('/knowledge/remove_collection', {
      dataset_id: data.knowledgeId,
      document_id: id,
    })
    getCollections()
  }

  const uploadSuccess = res => {
    data.files.push(res.data)
  }

  const getCollections = async (loading = true) => {
    loading && (data.showCollectionsLoading = true)
    const res = await http.post('/knowledge/collection', {
      id: data.knowledgeId,
    })
    data.collections = res.data.data
    loading && (data.showCollectionsLoading = false)
    !loading && console.log('刷新知识库状态')
  }

  let refreshCollectionsTimer = null
  const refreshCollection = () => {
    refreshCollectionsTimer = setInterval(() => {
      getCollections(false)
    }, 2000)
  }
  const clearRefreshCollection = () => {
    clearInterval(refreshCollectionsTimer)
  }

  const showKnowledge = row => {
    data.knowledgeId = row.id
    getCollections()
    data.knowledgeName = row.name
    data.showKnowledge = true
    refreshCollection()
  }

  const closeKnowledge = () => {
    data.showKnowledge = false
    clearRefreshCollection()
  }

  const getList = async () => {
    const res = await http.post('/knowledge/list')
    data.list = res.data.data
  }

  onMounted(() => {
    getList()
  })

  const settingsOK = async () => {
    const res = await http.post('/knowledge/set_settings', data.settings)
    ElMessage.success('保存成功')
    data.showSettings = false
    getList()
  }
</script>

<style scoped>
  .knowledge-toolbar {
    display: flex;
    justify-content: right;
    margin-bottom: 10px;
  }
</style>
