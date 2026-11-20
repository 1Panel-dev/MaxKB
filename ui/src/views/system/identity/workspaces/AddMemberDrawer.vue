<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CreateWorkspaceMemberPayload, ListItem, SystemUserOption, WorkspaceItem } from '@/api/types'
import type { FormInstance } from 'element-plus'
import { ROLE_TYPE } from '@/api/enums'
import CurrentUserApi from '@/api/admin/auth/current-user'
import CommonSystemApi from '@/api/admin/system/common'
import WorkspaceApi from '@/api/admin/system/workspace'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'AddWorkspaceMemberDrawer' })

const props = defineProps<{ currentWorkspace?: WorkspaceItem }>()

const emit = defineEmits<{ refresh: [workspaceId: string] }>()
const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const memberForm = reactive<{ members: CreateWorkspaceMemberPayload[] }>({ members: [] })

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
      userOptions.value = [...new Map([...selectedUserOptions, ...users].map((user) => [user.id, user])).values()]
    })
    .finally(() => {
      userOptionsLoading.value = false
    })
}

function loadRoleOptions() {
  roleOptionsLoading.value = true
  return CurrentUserApi.getCurrentUserRoleList()
    .then((roles) => {
      roleOptions.value = roles.filter((role) => role.type !== ROLE_TYPE.ADMIN)
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
      memberForm.members.map((member) => ({ role_ids: [...member.role_ids], user_ids: [...member.user_ids] })),
    )
      .then(() => {
        MsgSuccess(t('common.messages.addSuccess'))
        emit('refresh', workspaceId)
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
  <MkDrawer v-model="visible" :title="t('system.member.add')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="memberForm"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <MkFormList v-model="memberForm.members" :add-text="t('system.member.add')" :default-item="{ role_ids: [], user_ids: [] }">
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
              remote-show-suffix
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
            class="flex-1 small"
            :label="index === 0 ? t('user.role.label') : ''"
            :prop="`members.${index}.role_ids`"
            :rules="{ required: true, type: 'array', min: 1, message: t('user.role.requiredMessage'), trigger: 'change' }"
          >
            <el-select
              v-model="memberSetting.role_ids"
              :loading="roleOptionsLoading"
              collapse-tags
              collapse-tags-tooltip
              filterable
              fit-input-width
              multiple
              :placeholder="t('user.role.placeholder')"
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
      <!-- 取消添加成员 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 添加工作空间成员 -->
      <el-button type="primary" :loading="loading" @click="submit">{{ t('common.actions.add') }}</el-button>
    </template>
  </MkDrawer>
</template>
