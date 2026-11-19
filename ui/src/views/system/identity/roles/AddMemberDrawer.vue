<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CreateRoleMemberItem, RoleItem, SystemUserOption, WorkspaceItem } from '@/api/types'
import type { FormInstance } from 'element-plus'
import { ROLE_TYPE } from '@/api/enums'
import CommonSystemApi from '@/api/admin/system/common'
import RoleApi from '@/api/admin/system/role'
import WorkspaceApi from '@/api/admin/system/workspace'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'AddRoleMemberDrawer' })

const props = defineProps<{ currentRole: RoleItem }>()
const emit = defineEmits<{ refresh: [] }>()
const { auth } = useStore()
const { t } = useI18n({ useScope: 'global' })

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
      userOptions.value = [...new Map([...selectedUserOptions, ...users].map((user) => [user.id, user])).values()]
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
      workspace_ids: props.currentRole.type === ROLE_TYPE.ADMIN ? ['None'] : auth.isPE ? ['default'] : [...(member.workspace_ids ?? [])],
    }))

    loading.value = true
    RoleApi.postRoleMembers(props.currentRole.id, { members })
      .then(() => {
        MsgSuccess(t('common.messages.addSuccess'))
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
  <MkDrawer v-model="visible" :title="t('system.member.add')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="memberForm"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <MkFormList v-model="memberForm.members" :add-text="t('system.member.add')" :default-item="{ user_ids: [], workspace_ids: [] }">
        <template #default="{ index, item: memberSetting }">
          <el-form-item
            class="flex-1 small"
            :label="index === 0 ? t('system.member.label') : ''"
            :prop="`members.${index}.user_ids`"
            :rules="{ required: true, type: 'array', min: 1, message: t('system.member.requiredMessage'), trigger: 'change' }"
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
              :placeholder="t('system.member.placeholder')"
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
            class="flex-1 small"
            :label="index === 0 ? t('workspace.title') : ''"
            :prop="`members.${index}.workspace_ids`"
            :rules="{ required: true, type: 'array', min: 1, message: t('user.workspace.requiredMessage'), trigger: 'change' }"
          >
            <el-select
              v-model="memberSetting.workspace_ids"
              :loading="workspaceOptionsLoading"
              collapse-tags
              collapse-tags-tooltip
              filterable
              fit-input-width
              multiple
              :placeholder="t('user.workspace.placeholder')"
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
      <!-- 取消添加角色成员 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 添加角色成员 -->
      <el-button type="primary" :loading="loading" @click="submit">{{ t('common.actions.add') }}</el-button>
    </template>
  </MkDrawer>
</template>
