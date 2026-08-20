<script setup lang="ts">
import { ref, useTemplateRef, watch } from 'vue'
import RoleApi from '@/api/admin/system/role'
import { ROLE_TYPE } from '@/api/enums'
import type { OptionItem, RequestParams, RoleItem, RoleMember } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import AddMemberDrawer from '../AddMemberDrawer.vue'

const props = defineProps<{ currentRole: RoleItem }>()
const loading = ref(false)
const members = ref<RoleMember[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<RequestParams>()
const searchFields: OptionItem<string>[] = [
  { label: '用户名', value: 'username' },
  { label: '姓名', value: 'nick_name' },
]

function loadMembers(reset = false) {
  if (reset) paginationConfig.value.currentPage = 1
  loading.value = true
  return RoleApi.getRoleMemberList(props.currentRole.id, paginationConfig.value, searchQuery.value)
    .then(({ records, total }) => {
      members.value = records
      paginationConfig.value.total = total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearch(query?: RequestParams) {
  searchQuery.value = query
  loadMembers(true)
}

// 添加成员

const addMemberDrawerRef =
  useTemplateRef<InstanceType<typeof AddMemberDrawer>>('addMemberDrawerRef')
function handleOpenAddMemberDrawer() {
  addMemberDrawerRef.value?.open()
}

function handleMemberAdded() {
  loadMembers(true)
}

// 移除成员
function handleRemoveMember(member: RoleMember) {
  MsgConfirm(`确定移除成员“${member.nick_name || member.username}”吗？`)
    .then(() => {
      loading.value = true
      return RoleApi.deleteRoleMember(props.currentRole.id, member.user_relation_id).then(() => {
        MsgSuccess('移除成功')
        return loadMembers()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

/* 批量删除成员 */
const batchSelectedMembers = ref<RoleMember[]>([])
function handleBatchDelete() {
  MsgConfirm(`是否删除选中的 ${batchSelectedMembers.value.length} 个成员？`, '')
    .then(() => {
      // TODO: 批量删除
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleBatchSelectionChange(selection: unknown[]) {
  batchSelectedMembers.value = selection as RoleMember[]
}

watch(
  () => props.currentRole.id,
  () => loadMembers(true),
  { immediate: true },
)
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <div class="flex-between mb-4">
      <el-button type="primary" @click="handleOpenAddMemberDrawer">
        <MkIcon name="icon_add_outlined" />添加成员
      </el-button>
      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      v-model:pagination-config="paginationConfig"
      v-loading="loading"
      :data="members"
      :isSearching="Boolean(searchQuery)"
      @current-change="loadMembers()"
      @size-change="loadMembers()"
      :max-table-height="290"
      @selection-change="handleBatchSelectionChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="nick_name" label="姓名" min-width="180" show-overflow-tooltip />
      <el-table-column prop="username" label="用户名" min-width="180" show-overflow-tooltip />
      <el-table-column
        v-if="currentRole.type !== ROLE_TYPE.ADMIN"
        prop="workspace_name"
        label="工作空间"
        min-width="180"
        show-overflow-tooltip
      />
      <el-table-column label="操作" width="70" fixed="right">
        <template #default="{ row }">
          <el-tooltip content="移除" placement="top">
            <el-button type="primary" text @click="handleRemoveMember(row)"
              ><MkIcon name="icon_assigned_outlined"
            /></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
      <template #footer-batch-actions>
        <el-button type="danger" plain @click="handleBatchDelete">移除</el-button>
      </template>
    </MkTable>
  </div>
  <AddMemberDrawer
    ref="addMemberDrawerRef"
    :current-role="currentRole"
    @refresh="handleMemberAdded"
  />
</template>
