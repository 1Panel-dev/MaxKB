<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import CommonSystemApi from '@/api/admin/system/common'
import RoleApi from '@/api/admin/system/role'
import WorkspaceApi from '@/api/admin/system/workspace'
import { ROLE_TYPE } from '@/api/enums'
import type { CreateRoleMemberItem, RoleItem, SystemUserOption, WorkspaceItem } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import MkFormList from '@/components/mk-form-list/index.vue'

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
      <MkFormList
        v-model="memberForm.members"
        add-text="添加成员"
        :default-item="{ user_ids: [], workspace_ids: [] }"
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
            v-if="showWorkspace"
            class="flex-1"
            :label="index === 0 ? '工作空间' : ''"
            :prop="`members.${index}.workspace_ids`"
            :rules="{
              required: true,
              type: 'array',
              min: 1,
              message: '请选择工作空间',
              trigger: 'change',
            }"
          >
            <el-select
              v-model="memberSetting.workspace_ids"
              :loading="workspaceOptionsLoading"
              collapse-tags
              collapse-tags-tooltip
              filterable
              fit-input-width
              multiple
              placeholder="请选择工作空间"
              :reserve-keyword="false"
            >
              <el-option
                v-for="workspaceOption in workspaceOptions"
                :key="workspaceOption.id"
                :label="workspaceOption.name"
                :title="workspaceOption.name"
                :value="workspaceOption.id"
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
