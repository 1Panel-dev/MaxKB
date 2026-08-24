<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CurrentUserApi from '@/api/admin/auth/current-user'
import CommonSystemApi from '@/api/admin/system/common'
import WorkspaceApi from '@/api/admin/system/workspace'
import type {
  CreateWorkspaceMemberPayload,
  ListItem,
  SystemUserOption,
  WorkspaceItem,
} from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import MkFormList from '@/components/mk-form-list/index.vue'

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
const memberForm = reactive<{ members: CreateWorkspaceMemberPayload[] }>({
  members: [],
})

/* 成员与角色选项 */
const userOptions = ref<SystemUserOption[]>([])
const userOptionsLoading = ref(false)
const roleOptions = ref<ListItem[]>([])
const roleOptionsLoading = ref(false)

function loadUserOptions(keyword = '') {
  userOptionsLoading.value = true
  return CommonSystemApi.getAllUsers(keyword ? { nick_name: keyword } : undefined)
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
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
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
      <MkFormList
        v-model="memberForm.members"
        add-text="添加成员"
        :default-item="{ role_ids: [], user_ids: [] }"
      >
        <template #default="{ index, item: memberSetting }">
          <el-form-item
            class="flex-1"
            :label="index === 0 ? '成员' : ''"
            :prop="`members.${index}.user_ids`"
            :rules="{
              required: true,
              type: 'array',
              min: 1,
              message: '请选择成员',
              trigger: 'change',
            }"
          >
            <el-select
              v-model="memberSetting.user_ids"
              :loading="userOptionsLoading"
              :remote-method="loadUserOptions"
              collapse-tags
              collapse-tags-tooltip
              filterable
              fit-input-width
              multiple
              placeholder="请选择成员"
              remote
              :reserve-keyword="false"
            >
              <el-option
                v-for="userOption in userOptions"
                :key="userOption.id"
                :label="userOption.nick_name || userOption.username"
                :title="userOption.nick_name || userOption.username"
                :value="userOption.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            class="flex-1"
            :label="index === 0 ? '角色' : ''"
            :prop="`members.${index}.role_ids`"
            :rules="{
              required: true,
              type: 'array',
              min: 1,
              message: '请选择角色',
              trigger: 'change',
            }"
          >
            <el-select
              v-model="memberSetting.role_ids"
              :loading="roleOptionsLoading"
              collapse-tags
              collapse-tags-tooltip
              filterable
              fit-input-width
              multiple
              placeholder="请选择角色"
              :reserve-keyword="false"
            >
              <el-option
                v-for="roleOption in roleOptions"
                :key="roleOption.id"
                :label="roleOption.name"
                :title="roleOption.name"
                :value="roleOption.id"
              />
            </el-select>
          </el-form-item>
        </template>
      </MkFormList>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">添加</el-button>
    </template>
  </MkDrawer>
</template>
