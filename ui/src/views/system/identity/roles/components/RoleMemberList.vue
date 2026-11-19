<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, OptionItem, RoleItem, RoleMember } from '@/api/types'
import { ROLE_TYPE } from '@/api/enums'
import RoleApi from '@/api/admin/system/role'
import AddMemberDrawer from '../AddMemberDrawer.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import perm from '@/permission/index.ts'

const props = defineProps<{ currentRole: RoleItem }>()
const { t } = useI18n({ useScope: 'global' })
const loading = ref(false)
const members = ref<RoleMember[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchQuery = ref<Dict<unknown>>()
const searchFields = computed<OptionItem<string>[]>(() => [
  { label: t('user.username.label'), value: 'username' },
  { label: t('user.name.label'), value: 'nick_name' },
])

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

function handleSearch(query?: Dict<unknown>) {
  searchQuery.value = query
  loadMembers(true)
}

// 添加成员

const addMemberDrawerRef = useTemplateRef<InstanceType<typeof AddMemberDrawer>>('addMemberDrawerRef')
function handleOpenAddMemberDrawer() {
  addMemberDrawerRef.value?.open()
}

function handleMemberAdded() {
  loadMembers(true)
}

// 移除成员
function handleRemoveMember(member: RoleMember) {
  MsgConfirm(`${t('system.member.removeTitle')}: ${member.nick_name || member.username}?`, '', { confirmButtonText: t('common.actions.remove') })
    .then(() => {
      loading.value = true
      return RoleApi.deleteRoleMember(props.currentRole.id, member.user_relation_id).then(() => {
        MsgSuccess(t('common.messages.removeSuccess'))
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
  MsgConfirm(`${t('system.member.batchRemoveTitle', { count: batchSelectedMembers.value.length }, batchSelectedMembers.value.length)}?`, '', {
    confirmButtonText: t('common.actions.remove'),
  })
    .then(() => {
      loading.value = true
      const memberIds = batchSelectedMembers.value.map((member) => member.user_relation_id)
      return RoleApi.deleteRoleMembers(props.currentRole.id, memberIds).then(() => {
        MsgSuccess(t('common.messages.removeSuccess'))
        return loadMembers()
      })
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
  <div class="flex-column min-h-0 flex-1">
    <div class="flex-between mb-4">
      <div>
        <!-- 添加成员 -->
        <el-button type="primary" v-if="perm.system.role.addMember()" @click="handleOpenAddMemberDrawer">
          <MkIcon name="icon_add_outlined" />
          {{ t('system.member.add') }}
        </el-button>
      </div>

      <MkComplexSearch :fields="searchFields" @change="handleSearch" />
    </div>
    <MkTable
      v-model:pagination-config="paginationConfig"
      v-loading="loading"
      :data="members"
      @current-change="loadMembers()"
      @size-change="loadMembers()"
      :max-table-height="290"
      @selection-change="handleBatchSelectionChange"
      rowKey="user_relation_id"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="nick_name" :label="t('user.name.label')" min-width="180" show-overflow-tooltip />
      <el-table-column prop="username" :label="t('user.username.label')" min-width="180" show-overflow-tooltip />
      <el-table-column
        v-if="currentRole.type !== ROLE_TYPE.ADMIN"
        prop="workspace_name"
        :label="t('workspace.title')"
        min-width="180"
        show-overflow-tooltip
      />
      <el-table-column :label="t('common.labels.operation')" width="70" fixed="right">
        <template #default="{ row }">
          <!-- 移除角色成员 -->
          <MkTooltip :content="t('common.actions.remove')" placement="top" v-if="perm.system.role.removeMember()">
            <el-button type="primary" text @click="handleRemoveMember(row)"><MkIcon name="icon_assigned_outlined" /></el-button>
          </MkTooltip>
        </template>
      </el-table-column>
      <template #footer-batch-actions>
        <!-- 批量移除角色成员 -->
        <el-button v-if="perm.system.role.removeMember()" type="danger" plain @click="handleBatchDelete">{{ t('common.actions.remove') }}</el-button>
      </template>
    </MkTable>
  </div>
  <AddMemberDrawer ref="addMemberDrawerRef" :current-role="currentRole" @refresh="handleMemberAdded" />
</template>
