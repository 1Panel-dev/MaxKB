<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex items-center justify-between mb-3 shrink-0">
      <el-button size="small" type="primary" @click="openAddMember">添加成员</el-button>
      <div class="flex items-center gap-2">
        <el-select v-model="searchType" size="small" style="width:90px">
          <el-option label="用户名" value="username" />
          <el-option label="昵称" value="nick_name" />
        </el-select>
        <el-input
          v-model="searchForm[searchType]"
          placeholder="搜索"
          clearable
          size="small"
          style="width:200px"
          @change="getList"
        />
      </div>
    </div>
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      stripe
      size="small"
      style="width:100%"
      max-height="calc(100vh - 420px)"
    >
      <el-table-column prop="nick_name" label="昵称" min-width="150" />
      <el-table-column prop="username" label="用户名" min-width="150" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button text type="danger" size="small" @click="handleDelete(row)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="flex justify-end mt-3 shrink-0">
      <el-pagination
        v-model:current-page="pagination.current_page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        size="small"
        @size-change="onPageSizeChange"
        @current-change="getList"
      />
    </div>
    <AddMemberDrawer ref="addMemberDrawerRef" :currentRole="props.currentRole" @refresh="getList" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import roleApi from '@/api/system/role'
import type { RoleItem } from '@/api/type/role'
import AddMemberDrawer from './AddMemberDrawer.vue'

const props = defineProps<{ currentRole?: RoleItem }>()

const loading = ref(false)
const searchType = ref('username')
const searchForm = reactive<Record<string, any>>({ username: '', nick_name: '' })
const pagination = reactive({ current_page: 1, page_size: 20, total: 0 })
const tableData = ref<any[]>([])
const addMemberDrawerRef = ref()

function onPageSizeChange() {
  pagination.current_page = 1
  getList()
}

async function getList() {
  if (!props.currentRole?.id) return
  loading.value = true
  try {
    const params = { [searchType.value]: searchForm[searchType.value] }
    const res = await roleApi.getRoleMemberList(props.currentRole.id, pagination, params, loading)
    tableData.value = res.data?.records || []
    pagination.total = res.data?.total || 0
  } catch { tableData.value = [] }
}

function openAddMember() {
  addMemberDrawerRef.value?.open()
}

function handleDelete(row: any) {
  ElMessageBox.confirm(`确认移除「${row.nick_name}」吗？`, '提示', {
    confirmButtonText: '移除',
    confirmButtonClass: 'danger',
    type: 'warning',
  }).then(() => {
    roleApi.deleteRoleMember(props.currentRole?.id as string, row.user_relation_id).then(() => {
      ElMessage.success('移除成功')
      getList()
    })
  }).catch(() => {})
}

watch(() => props.currentRole?.id, getList)
onMounted(getList)
</script>
