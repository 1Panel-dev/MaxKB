<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">用户管理</span>
    </div>
    <el-card class="flex-1 flex flex-col overflow-hidden" style="--el-card-padding:16px">
      <!-- Toolbar -->
      <div class="flex items-center justify-between mb-4 shrink-0 flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <el-button size="small" type="primary" @click="createUser">创建用户</el-button>
          <el-button size="small" :disabled="!multipleSelection.length" @click="handleBatchDelete">批量删除</el-button>
        </div>
        <div class="flex items-center gap-2">
          <el-select v-model="searchType" size="small" style="width:100px" @change="onSearchTypeChange">
            <el-option label="用户名" value="username" />
            <el-option label="昵称" value="nick_name" />
            <el-option label="邮箱" value="email" />
            <el-option label="状态" value="is_active" />
          </el-select>
          <el-input
            v-if="searchType === 'username' || searchType === 'nick_name' || searchType === 'email'"
            v-model="searchForm[searchType]"
            placeholder="搜索"
            clearable
            size="small"
            style="width:200px"
            @change="fetchList"
          />
          <el-select
            v-else-if="searchType === 'is_active'"
            v-model="searchForm.is_active"
            placeholder="选择状态"
            clearable
            size="small"
            style="width:200px"
            @change="fetchList"
          >
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
        </div>
      </div>

      <!-- Table -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="list"
        border
        stripe
        size="small"
        style="width:100%"
        max-height="calc(100vh - 320px)"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="44" />
        <el-table-column prop="nick_name" label="昵称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="90">
          <template #default="{ row }">
            <span v-if="row.is_active" class="text-green-600 flex items-center gap-1 text-sm">
              <el-icon><SuccessFilled /></el-icon> 启用
            </span>
            <span v-else class="text-gray-400 flex items-center gap-1 text-sm">
              <el-icon><WarningFilled /></el-icon> 停用
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.email || '-' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120">
          <template #default="{ row }">{{ row.phone || '-' }}</template>
        </el-table-column>
        <el-table-column label="角色" min-width="160">
          <template #default="{ row }">
            <span v-if="row.role_names?.length" class="flex flex-wrap gap-1">
              <el-tag v-for="r in row.role_names" :key="r" size="small">{{ r }}</el-tag>
            </span>
            <span v-else class="text-gray-400 text-sm">-</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-switch
              size="small"
              :model-value="row.is_active"
              :before-change="() => toggleStatus(row)"
              :disabled="row.role === 'ADMIN'"
              class="mr-2"
            />
            <el-button text type="primary" size="small" @click="editUser(row)">编辑</el-button>
            <el-button text type="primary" size="small" @click="editPwd(row)">密码</el-button>
            <el-button text type="danger" size="small" :disabled="row.role === 'ADMIN'" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="flex justify-end mt-4 shrink-0">
        <el-pagination
          v-model:current-page="pagination.current_page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          size="small"
          @size-change="onPageSizeChange"
          @current-change="fetchList"
        />
      </div>
    </el-card>

    <UserDrawer ref="userDrawerRef" @refresh="fetchList" />
    <UserPwdDialog ref="userPwdDialogRef" @refresh="fetchList" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import userApi from '@/api/system/user-manage'
import UserDrawer from './component/UserDrawer.vue'
import UserPwdDialog from './component/UserPwdDialog.vue'

const loading = ref(false)
const list = ref<any[]>([])
const pagination = reactive({ current_page: 1, page_size: 20, total: 0 })
const tableRef = ref()
const multipleSelection = ref<any[]>([])

const searchType = ref('username')
const searchForm = reactive<Record<string, any>>({ username: '', nick_name: '', email: '', is_active: null })

function formatTime(ts: string | null) {
  if (!ts) return '-'
  const d = new Date(ts)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function onSearchTypeChange() {
  searchForm.username = ''
  searchForm.nick_name = ''
  searchForm.email = ''
  searchForm.is_active = null
}

function onPageSizeChange() {
  pagination.current_page = 1
  fetchList()
}

function onSelectionChange(selection: any[]) {
  multipleSelection.value = selection
}

function buildParams() {
  const p: any = {}
  const val = searchForm[searchType.value]
  if (val !== undefined && val !== null && val !== '') {
    p[searchType.value] = val
  }
  return p
}

async function fetchList() {
  loading.value = true
  try {
    const res = await userApi.getUserManage(pagination, buildParams(), loading)
    pagination.total = res.data?.total ?? 0
    list.value = (res.data?.records ?? [])
      .map((u: any) => ({
        ...u,
        role_names: u.role_setting?.map((rs: any) => rs.role_name) || (u.role ? [u.role] : []),
      }))
  } catch { list.value = [] }
}

const userDrawerRef = ref()
function createUser() { userDrawerRef.value?.open() }
function editUser(row: any) { userDrawerRef.value?.open(row) }

const userPwdDialogRef = ref()
function editPwd(row: any) { userPwdDialogRef.value?.open(row) }

async function toggleStatus(row: any) {
  try {
    await userApi.putUserManage(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    fetchList()
    return true
  } catch { return false }
}

function deleteUser(row: any) {
  if (row.role === 'ADMIN') {
    ElMessage.warning('系统管理员不可删除')
    return
  }
  ElMessageBox.confirm(`确认删除「${row.nick_name}」吗？`, '提示', {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger',
    type: 'warning',
  }).then(() => {
    userApi.delUserManage(row.id).then(() => {
      ElMessage.success('删除成功')
      fetchList()
    })
  }).catch(() => {})
}

function handleBatchDelete() {
  if (!multipleSelection.value.length) return
  ElMessageBox.confirm(`确认删除选中的 ${multipleSelection.value.length} 个用户吗？`, '提示', {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger',
    type: 'warning',
  }).then(() => {
    userApi.batchDelete(multipleSelection.value.map((r) => r.id)).then(() => {
      ElMessage.success('删除成功')
      fetchList()
    })
  }).catch(() => {})
}

onMounted(fetchList)
</script>
