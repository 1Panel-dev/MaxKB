<template>
  <div class="p-5 h-full flex flex-col">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-lg font-semibold" style="color:var(--mk-N900)">应用资源</span>
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
          <el-option label="高级" value="WORK_FLOW" />
          <el-option label="简易" value="SIMPLE" />
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
              <el-avatar v-if="row.icon" shape="square" :size="24" style="background:none">
                <img :src="row.icon" alt="" />
              </el-avatar>
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'WORK_FLOW'" size="small" type="warning">高级</el-tag>
            <el-tag v-else size="small" type="primary">简易</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_publish" label="状态" width="100">
          <template #default="{ row }">
            <span v-if="row.is_publish" class="text-green-600 flex items-center gap-1">
              <el-icon><SuccessFilled /></el-icon> 已发布
            </span>
            <span v-else class="text-gray-400 flex items-center gap-1">
              <el-icon><WarningFilled /></el-icon> 未发布
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
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, row)">
              <el-button text type="primary" size="small">
                <MkIcon name="icon_more_outlined" :size="16" />
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="setting" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+SETTING')">
                    设置
                  </el-dropdown-item>
                  <el-dropdown-item command="auth" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+AUTH')">
                    资源授权
                  </el-dropdown-item>
                  <el-dropdown-item command="relate" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+RELATE_VIEW')">
                    查看关联资源
                  </el-dropdown-item>
                  <el-dropdown-item command="trigger" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+TRIGGER_READ')">
                    触发器
                  </el-dropdown-item>
                  <el-dropdown-item command="move" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+TRANSFER')">
                    转移到
                  </el-dropdown-item>
                  <el-dropdown-item command="export" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+EXPORT')">
                    导出
                  </el-dropdown-item>
                  <el-dropdown-item divided command="delete" v-if="hasPerm('SYSTEM_RESOURCE_APPLICATION:READ+DELETE')">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
import { hasPerm } from '@/composables/usePermission'

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
    const res = await resourceApi.getApplicationList(pagination, buildParams(), loading)
    pagination.total = res.data?.total ?? 0
    list.value = res.data?.records ?? []
  } catch { /* handled */ }
}

async function fetchUsers(query: string) {
  try {
    const res = await resourceApi.listUsers(query || '')
    userOptions.value = res.data ?? []
  } catch {
    userOptions.value = []
  }
}

function handleCommand(cmd: string, row: any) {
  switch (cmd) {
    case 'setting':
      ElMessage.info('设置功能待实现')
      break
    case 'auth':
      ElMessage.info('资源授权功能待实现')
      break
    case 'relate':
      ElMessage.info('查看关联资源管理功能待实现')
      break
    case 'trigger':
      ElMessage.info('触发器功能待实现')
      break
    case 'move':
      ElMessage.info('转移到功能待实现')
      break
    case 'export':
      handleExport(row)
      break
    case 'delete':
      handleDelete(row)
      break
  }
}

async function handleExport(row: any) {
  try {
    await resourceApi.exportApplication(row.id, row.name)
    ElMessage.success('导出成功')
  } catch { /* handled */ }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await resourceApi.delApplication(row.id)
    ElMessage.success('删除成功')
    fetchList()
  } catch { /* cancelled or error */ }
}

onMounted(() => {
  fetchList()
  fetchUsers('')
})
</script>
