<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">工具资源</span>
    </div>
    <el-card class="flex-1 flex flex-col overflow-hidden" style="--el-card-padding: 16px">
      <!-- Search -->
      <div class="flex items-center gap-3 mb-4 flex-wrap">
        <el-select v-model="searchType" style="width: 120px" size="small" @change="onSearchTypeChange">
          <el-option label="名称" value="name" />
          <el-option label="创建人" value="create_user" />
          <el-option label="类型" value="tool_type" />
          <el-option label="来源" value="source" />
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
          v-else-if="searchType === 'tool_type'"
          v-model="searchForm.tool_type"
          placeholder="选择类型"
          clearable
          size="small"
          style="width: 220px"
          @change="fetchList"
        >
          <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-select
          v-else-if="searchType === 'source'"
          v-model="searchForm.source"
          placeholder="选择来源"
          clearable
          size="small"
          style="width: 220px"
          @change="fetchList"
        >
          <el-option label="内置" value="TOOL_STORE" />
          <el-option label="自定义" value="CUSTOM" />
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
        <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <MkIcon name="icon_folder_outlined" :size="20" />
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="tool_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.tool_type === 'MCP'" size="small">MCP</el-tag>
            <el-tag v-else-if="row.tool_type === 'DATA_SOURCE'" size="small" type="success">数据源</el-tag>
            <el-tag v-else-if="row.tool_type === 'SKILL'" size="small" type="info">Skills</el-tag>
            <el-tag v-else-if="row.tool_type === 'WORKFLOW'" size="small" type="warning">工作流</el-tag>
            <el-tag v-else size="small" type="primary">自定义</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100">
          <template #default="{ row }">
            {{ row.template_id ? '内置' : '自定义' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <span v-if="row.is_active" class="text-green-600 flex items-center gap-1">
              <el-icon><SuccessFilled /></el-icon> 启用
            </span>
            <span v-else class="text-gray-400 flex items-center gap-1">
              <el-icon><WarningFilled /></el-icon> 停用
            </span>
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
const searchForm = reactive({ name: '', create_user: '', tool_type: '', source: '' })
const userOptions = ref<any[]>([])

const typeOptions = [
  { label: 'MCP', value: 'MCP' },
  { label: '数据源', value: 'DATA_SOURCE' },
  { label: '自定义', value: 'CUSTOM' },
  { label: 'Skills', value: 'SKILL' },
  { label: '工具工作流', value: 'WORKFLOW' },
]

function formatTime(ts: string | null) {
  if (!ts) return '-'
  const d = new Date(ts)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function onSearchTypeChange() {
  searchForm.name = ''
  searchForm.create_user = ''
  searchForm.tool_type = ''
  searchForm.source = ''
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
    const res = await resourceApi.getToolList(pagination, buildParams(), loading)
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
    await resourceApi.delTool(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch { /* cancelled or error */ }
}

onMounted(() => {
  fetchList()
  fetchUsers('')
})
</script>
