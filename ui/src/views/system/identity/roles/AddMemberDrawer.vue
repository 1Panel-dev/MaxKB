<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
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
import MemberWorkspaceSetting from './components/MemberWorkspaceSetting.vue'

defineOptions({ name: 'AddRoleMemberDrawer' })

const props = defineProps<{ currentRole: RoleItem }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const memberForm = reactive<{ members: CreateRoleMemberItem[] }>({ members: [] })
const showWorkspace = computed(() => props.currentRole.type !== ROLE_TYPE.ADMIN && auth.isEE)

/* 成员与工作空间选项 */
const userOptions = ref<SystemUserOption[]>([])
const userOptionsLoading = ref(false)
const workspaceOptions = ref<WorkspaceItem[]>([])
const workspaceOptionsLoading = ref(false)

function loadUserOptions(keyword = '') {
  userOptionsLoading.value = true
  return UserManageApi.getAllUsers(keyword ? { nick_name: keyword } : undefined)
    .then((users) => {
      const selectedUserIds = new Set(memberForm.members.flatMap(({ user_ids }) => user_ids))
      const selectedUserOptions = userOptions.value.filter(({ id }) => selectedUserIds.has(id))
      userOptions.value = [
        ...new Map([...selectedUserOptions, ...users].map((user) => [user.id, user])).values(),
      ]
    })
    .finally(() => {
      userOptionsLoading.value = false
    })
}

function loadWorkspaceOptions() {
  if (!showWorkspace.value) return Promise.resolve()

  workspaceOptionsLoading.value = true
  return WorkspaceApi.getSystemWorkspaceList()
    .then((workspaces) => {
      workspaceOptions.value = workspaces
    })
    .finally(() => {
      workspaceOptionsLoading.value = false
    })
}

function open() {
  memberForm.members = [{ user_ids: [], workspace_ids: [] }]
  visible.value = true
  return Promise.all([loadUserOptions(), loadWorkspaceOptions()])
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    const members = memberForm.members.map((member) => ({
      user_ids: [...member.user_ids],
      workspace_ids:
        props.currentRole.type === ROLE_TYPE.ADMIN
          ? ['None']
          : auth.isPE
            ? ['default']
            : [...(member.workspace_ids ?? [])],
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

function close() {
  visible.value = false
  resetData()
}

function resetData() {
  memberForm.members = []
  loading.value = false
  userOptions.value = []
  userOptionsLoading.value = false
  workspaceOptions.value = []
  workspaceOptionsLoading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="添加成员" @closed="resetData">
    <el-form ref="formRef" :model="memberForm" label-position="top">
      <MemberWorkspaceSetting
        v-model="memberForm.members"
        :remote-user-method="loadUserOptions"
        :show-workspace="showWorkspace"
        :user-loading="userOptionsLoading"
        :user-options="userOptions"
        :workspace-loading="workspaceOptionsLoading"
        :workspace-options="workspaceOptions"
      />
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDrawer>
</template>
