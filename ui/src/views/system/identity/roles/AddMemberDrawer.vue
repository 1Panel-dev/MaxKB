<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import RoleApi from '@/api/admin/system/role'
import UserManageApi from '@/api/admin/system/user-manage'
import WorkspaceApi from '@/api/admin/system/workspace'
import {
  ROLE_TYPE,
  type CreateRoleMemberItem,
  type RoleItem,
  type SystemUserOption,
  type WorkspaceItem,
} from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{ currentRole: RoleItem }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()

const visible = ref(false)
const loading = ref(false)
const optionsLoading = ref(false)
const formRef = ref<FormInstance>()
const memberRows = reactive<CreateRoleMemberItem[]>([])
const userOptions = ref<SystemUserOption[]>([])
const workspaceOptions = ref<WorkspaceItem[]>([])
const showWorkspace = computed(() => props.currentRole.type !== ROLE_TYPE.ADMIN && auth.isEE)
const rules: FormRules = {
  user_ids: [{ required: true, message: '请选择用户', trigger: 'change' }],
  workspace_ids: [{ required: true, message: '请选择工作空间', trigger: 'change' }],
}
let searchTimer: ReturnType<typeof setTimeout> | null = null

function createEmptyRow(): CreateRoleMemberItem {
  return { user_ids: [], ...(showWorkspace.value ? { workspace_ids: [] } : {}) }
}

function loadOptions(query?: string) {
  optionsLoading.value = true
  return Promise.all([
    UserManageApi.getAllUsers(query ? { nick_name: query } : undefined),
    showWorkspace.value ? WorkspaceApi.getSystemWorkspaceList() : Promise.resolve([]),
  ])
    .then(([users, workspaces]) => {
      userOptions.value = users
      workspaceOptions.value = workspaces
    })
    .finally(() => {
      optionsLoading.value = false
    })
}

function handleRemoteSearch(query: string) {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadOptions(query), 300)
}

function handleAddRow() {
  memberRows.push(createEmptyRow())
}

function handleDeleteRow(index: number) {
  if (memberRows.length > 1) memberRows.splice(index, 1)
}

function resetData() {
  memberRows.splice(0, memberRows.length, createEmptyRow())
  userOptions.value = []
  workspaceOptions.value = []
  loading.value = false
  optionsLoading.value = false
  formRef.value?.clearValidate()
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
}

function open() {
  resetData()
  visible.value = true
  loadOptions()
}

function close() {
  visible.value = false
  resetData()
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    const members = memberRows.map((row) => ({
      user_ids: row.user_ids,
      workspace_ids:
        props.currentRole.type === ROLE_TYPE.ADMIN
          ? ['None']
          : auth.isPE
            ? ['default']
            : row.workspace_ids,
    }))
    loading.value = true
    RoleApi.postRoleMembers(props.currentRole.id, { members })
      .then(() => {
        MsgSuccess('添加成功')
        emit('refresh')
        close()
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="添加成员" size="600" @closed="resetData">
    <el-form ref="formRef" :model="memberRows" label-position="top">
      <el-scrollbar>
        <div v-for="(row, index) in memberRows" :key="index" class="mb-3 flex items-end gap-2">
          <el-form-item
            :label="index === 0 ? '用户' : ''"
            :prop="`${index}.user_ids`"
            :rules="rules.user_ids"
            class="mb-0 flex-1"
          >
            <el-select
              v-model="row.user_ids"
              class="w-full"
              filterable
              remote
              multiple
              collapse-tags
              collapse-tags-tooltip
              reserve-keyword
              :remote-method="handleRemoteSearch"
              :loading="optionsLoading"
              placeholder="请选择用户"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.id"
                :label="user.nick_name || user.username"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="showWorkspace"
            :label="index === 0 ? '工作空间' : ''"
            :prop="`${index}.workspace_ids`"
            :rules="rules.workspace_ids"
            class="mb-0 flex-1"
          >
            <el-select
              v-model="row.workspace_ids"
              class="w-full"
              filterable
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="请选择工作空间"
            >
              <el-option
                v-for="workspace in workspaceOptions"
                :key="workspace.id"
                :label="workspace.name"
                :value="workspace.id"
              />
            </el-select>
          </el-form-item>
          <el-button text :disabled="memberRows.length === 1" @click="handleDeleteRow(index)"
            ><MkIcon name="icon_delete-trash_outlined"
          /></el-button>
        </div>
      </el-scrollbar>
      <el-button text type="primary" @click="handleAddRow"
        ><MkIcon name="icon_add_outlined" />添加</el-button
      >
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDrawer>
</template>
