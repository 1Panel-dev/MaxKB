<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">知识库资源</span>
    </div>
    <el-card class="flex-1 flex flex-col overflow-hidden" style="--el-card-padding: 16px">
      <!-- Search -->
      <div class="flex items-center gap-3 mb-4 flex-wrap">
        <el-select v-model="searchType" style="width: 120px" size="small" @change="onSearchTypeChange">
          <el-option label="名称" value="name" />
          <el-option label="创建人" value="create_user" />
          <el-option label="类型" value="type" />
        </el-select>
        <el-input
          v-if="searchType === 'name'"
          v-model="searchForm.name"
          placeholder="搜索"
          clearable
          size="small"
          style="width: 220px"
          @change="fetchList"
        />
        <el-select
          v-else-if="searchType === 'create_user'"
          v-model="searchForm.create_user"
          placeholder="选择创建人"
          clearable
          filterable
          remote
          size="small"
          style="width: 220px"
          :remote-method="fetchUsers"
          @change="fetchList"
        >
          <el-option v-for="u in userOptions" :key="u.id" :value="u.id" :label="u.nick_name" />
        </el-select>
        <el-select
          v-else-if="searchType === 'type'"
          v-model="searchForm.type"
          placeholder="选择类型"
          clearable
          size="small"
          style="width: 220px"
          @change="fetchList"
        >
          <el-option label="通用知识库" value="0" />
          <el-option label="Web 知识库" value="1" />
          <el-option label="Lark 知识库" value="2" />
          <el-option label="工作流知识库" value="4" />
        </el-select>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        size="small"
        style="width: 100%"
        max-height="calc(100vh - 320px)"
      >
        <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <MkIcon name="icon_document_outlined" :size="20" />
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="130">
          <template #default="{ row }">
            <el-tag v-if="String(row.type) === '0'" size="small">通用</el-tag>
            <el-tag v-else-if="String(row.type) === '1'" size="small" type="success">Web</el-tag>
            <el-tag v-else-if="String(row.type) === '2'" size="small" type="info">Lark</el-tag>
            <el-tag v-else-if="String(row.type) === '4'" size="small" type="warning">工作流</el-tag>
            <span v-else class="text-gray-400 text-sm">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建人" width="120" />
        <el-table-column label="更新时间" width="170">
          <template #default="{ row }">{{ formatTime(row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="pagination.current_page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          size="small"
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import resourceApi from '@/api/system/resource'

const loading = ref(false)
const list = ref<any[]>([])
const pagination = reactive({ current_page: 1, page_size: 20, total: 0 })
const searchType = ref('name')
const searchForm = reactive({ name: '', create_user: '', type: '' })
const userOptions = ref<any[]>([])

function formatTime(ts: string | null) {
  if (!ts) return '-'
  const d = new Date(ts)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function onSearchTypeChange() {
  searchForm.name = ''
  searchForm.create_user = ''
  searchForm.type = ''
}

function buildParams() {
  const p: any = {}
  const val = searchForm[searchType.value as keyof typeof searchForm]
  if (val) p[searchType.value] = val
  return p
}

async function fetchList() {
  loading.value = true
  try {
    const res = await resourceApi.getKnowledgeList(pagination, buildParams(), loading)
    pagination.total = res.data?.total ?? 0
    list.value = res.data?.records ?? []
  } catch { /* handled by request */ }
}

async function fetchUsers(query: string) {
  try {
    const res = await resourceApi.listUsers(query || '')
    userOptions.value = res.data ?? []
  } catch {
    userOptions.value = []
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await resourceApi.delKnowledge(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch { /* cancelled or error */ }
}

onMounted(() => {
  fetchList()
  fetchUsers('')
})
</script>
