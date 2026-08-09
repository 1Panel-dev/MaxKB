<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import WorkspaceApi from '@/api/admin/system/workspace'
import type {
  CreateWorkspaceMemberParamsItem,
  SelectOption,
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
  saved: []
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
const roleOptions = ref<SelectOption[]>([])
const roleOptionsLoading = ref(false)
let userRequestSequence = 0

function loadUserOptions(keyword = '') {
  const requestSequence = ++userRequestSequence
  userOptionsLoading.value = true
  return UserManageApi.getAllUsers(keyword ? { nick_name: keyword } : undefined)
    .then((users) => {
      if (requestSequence !== userRequestSequence) return

      const selectedUserIds = new Set(memberForm.members.flatMap(({ user_ids }) => user_ids))
      const selectedUserOptions = userOptions.value.filter(({ id }) => selectedUserIds.has(id))
      userOptions.value = [
        ...new Map([...selectedUserOptions, ...users].map((user) => [user.id, user])).values(),
      ]
    })
    .finally(() => {
      if (requestSequence === userRequestSequence) userOptionsLoading.value = false
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
  nextTick(() => formRef.value?.clearValidate())
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
        visible.value = false
        emit('saved')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="添加成员">
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
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDrawer>
</template>
