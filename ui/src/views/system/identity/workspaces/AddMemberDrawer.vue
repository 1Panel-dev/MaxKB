<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import WorkspaceApi from '@/api/admin/system/workspace'
import type {
  CreateWorkspaceMemberParamsItem,
  ListItem,
  SystemUserOption,
  WorkspaceItem,
} from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import MemberRoleSetting from './components/MemberRoleSetting.vue'

defineOptions({ name: 'AddWorkspaceMemberDrawer' })

const props = defineProps<{
  currentWorkspace?: WorkspaceItem
}>()

const emit = defineEmits<{
  refresh: []
}>()

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const memberForm = reactive<{ members: CreateWorkspaceMemberParamsItem[] }>({
  members: [],
})

/* 成员与角色选项 */
const userOptions = ref<SystemUserOption[]>([])
const userOptionsLoading = ref(false)
const roleOptions = ref<ListItem[]>([])
const roleOptionsLoading = ref(false)

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

function loadRoleOptions() {
  roleOptionsLoading.value = true
  return CurrentUserApi.getCurrentUserRoleList()
    .then((roles) => {
      roleOptions.value = roles
    })
    .finally(() => {
      roleOptionsLoading.value = false
    })
}

function open() {
  memberForm.members = [{ role_ids: [], user_ids: [] }]
  visible.value = true
  return Promise.all([loadUserOptions(), loadRoleOptions()])
}

function submit() {
  const workspaceId = props.currentWorkspace?.id
  if (!workspaceId) return

  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    WorkspaceApi.postWorkspaceMembers(
      workspaceId,
      memberForm.members.map((member) => ({
        role_ids: [...member.role_ids],
        user_ids: [...member.user_ids],
      })),
    )
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
  roleOptions.value = []
  roleOptionsLoading.value = false
  userOptions.value = []
  userOptionsLoading.value = false
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="添加成员" @closed="resetData">
    <el-form ref="formRef" :model="memberForm" label-position="top">
      <MemberRoleSetting
        v-model="memberForm.members"
        :role-loading="roleOptionsLoading"
        :role-options="roleOptions"
        :user-loading="userOptionsLoading"
        :user-options="userOptions"
        :remote-user-method="loadUserOptions"
      />
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDrawer>
</template>
