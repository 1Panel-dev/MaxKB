<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUserSyncConflict, ListItem, LoginMethod, OptionItem } from '@/api/types'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import { LOGIN_METHOD } from '@/api/enums'
import ChatUserApi from '@/api/admin/system/chat-management/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-management/chat-user-groups'
import UserManageApi from '@/api/admin/system/user-manage'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ImportUsersDialog' })

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ refresh: [] }>()

const LOCAL_FILE_SOURCE = 'LOCAL_FILE' as const

interface ImportUsersForm {
  files: UploadUserFile[]
  syncType: string
  userGroupId: string
}

const dialogVisible = ref(false)

const importing = ref(false)
const importUsersFormRef = ref<FormInstance>()
const dragUploadRef = ref<InstanceType<typeof MkDragUpload>>()
const availableSyncTypes = ref<string[]>([])
const importUsersForm = reactive<ImportUsersForm>({ files: [], syncType: '', userGroupId: '' })
const importUsersFormRules = computed<FormRules<ImportUsersForm>>(() => ({
  files: [{ required: true, type: 'array', min: 1, message: t('upload.requiredMessage'), trigger: 'change' }],
  syncType: [{ required: true, message: t('user.source.requiredMessage'), trigger: 'change' }],
  userGroupId: [{ required: true, message: t('userGroup.requiredMessage'), trigger: 'change' }],
}))
const isLocalFileSource = computed(() => importUsersForm.syncType === LOCAL_FILE_SOURCE)
const canImport = computed(() => Boolean(importUsersForm.syncType) && (!isLocalFileSource.value || importUsersForm.files.length > 0))

/* 获取导入用户的来源类型 */
const syncTypesLoading = ref(false)
const userSourceLabels = computed<Record<LoginMethod | typeof LOCAL_FILE_SOURCE, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('user.source.local'),
  [LOGIN_METHOD.DINGTALK]: t('auth.login.options.dingtalk'),
  [LOGIN_METHOD.LARK]: t('auth.login.options.lark'),
  [LOGIN_METHOD.WECOM]: t('auth.login.options.wecom'),
  [LOCAL_FILE_SOURCE]: t('user.source.localFile'),
}))
const syncTypeOptions = computed<OptionItem<string>[]>(() =>
  availableSyncTypes.value.map((syncType) => ({
    label: userSourceLabels.value[syncType as keyof typeof userSourceLabels.value] ?? syncType,
    value: syncType,
  })),
)

function loadSyncTypes() {
  syncTypesLoading.value = true
  return ChatUserApi.getChatUserSyncTypes()
    .then((syncTypes) => {
      availableSyncTypes.value = [...syncTypes, LOCAL_FILE_SOURCE]
      importUsersForm.syncType = availableSyncTypes.value[0] ?? ''
    })
    .finally(() => {
      syncTypesLoading.value = false
    })
}

/* 用户组选项 */
const userGroupOptionsLoading = ref(false)
const userGroupOptions = ref<ListItem[]>([])
function loadUserGroupOptions() {
  userGroupOptionsLoading.value = true
  return ChatUserGroupsApi.getChatUserGroups()
    .then((groups) => {
      userGroupOptions.value = groups
    })
    .finally(() => {
      userGroupOptionsLoading.value = false
    })
}

function handleFileChange(file: UploadFile) {
  if (!/\.xlsx$/i.test(file.name)) {
    importUsersForm.files = []
    dragUploadRef.value?.clearFiles()
    MsgWarning(t('user.import.formatMessage'))
    return
  }

  importUsersForm.files = [file]
  nextTick(() => importUsersFormRef.value?.validateField('files'))
}

function handleFileRemove() {
  importUsersForm.files = []
  nextTick(() => importUsersFormRef.value?.validateField('files'))
}

function conflictTypeLabel(type: string) {
  if (type === 'username') return t('user.username.existsMessage')
  if (type === 'email') return t('user.email.existsMessage')
  if (type === 'nick_name') return t('user.name.existsMessage')
  return t('user.import.conflictMessage', { type })
}

function formatConflictMessage(conflicts: ChatUserSyncConflict[]) {
  return conflicts.map((conflict) => `${conflictTypeLabel(conflict.type)}: ${conflict.users.join('、')}`).join('；')
}

function handleDownloadTemplate() {
  UserManageApi.getUserManageImportTemplate()
}

/* 导入用户 */
function submitImportUsers() {
  if (!importUsersFormRef.value) return

  importUsersFormRef.value.validate((valid) => {
    if (!valid) return

    const syncFile = isLocalFileSource.value ? ((importUsersForm.files[0]?.raw ?? undefined) as File | undefined) : undefined
    importing.value = true
    return ChatUserApi.postSyncChatUsers(
      isLocalFileSource.value ? 'file' : importUsersForm.syncType,
      importUsersForm.userGroupId || undefined,
      syncFile,
    )
      .then((result) => {
        const conflictUsers = result.conflict_users ?? []
        const skippedCount = conflictUsers.reduce((sum, conflict) => sum + conflict.users.length, 0)
        const conflictMessage = formatConflictMessage(conflictUsers)
        const skipText = skippedCount > 0 ? `，${t('user.import.skippedMessage', { count: skippedCount }, skippedCount)}` : ''
        MsgSuccess(
          `${t('user.import.successMessage', { count: result.success_count }, result.success_count)}${skipText}${conflictMessage ? `，${conflictMessage}` : ''}`,
        )
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        importing.value = false
      })
  })
}

function open() {
  dialogVisible.value = true
  loadSyncTypes()
  loadUserGroupOptions()
}

function resetData() {
  Object.assign(importUsersForm, { files: [], syncType: '', userGroupId: '' })
  availableSyncTypes.value = []
  syncTypesLoading.value = false
  userGroupOptionsLoading.value = false
  userGroupOptions.value = []
  importing.value = false
  dragUploadRef.value?.clearFiles()
  importUsersFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('user.import.title')" @closed="resetData">
    <template #subtitle>{{ t('chatUser.import.description') }}</template>

    <el-form
      ref="importUsersFormRef"
      :model="importUsersForm"
      :rules="importUsersFormRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('user.source.label')" prop="syncType">
        <el-select v-model="importUsersForm.syncType" class="w-full" :loading="syncTypesLoading" :placeholder="t('user.source.placeholder')">
          <el-option
            v-for="syncTypeOption in syncTypeOptions"
            :key="syncTypeOption.value"
            :label="syncTypeOption.label"
            :value="syncTypeOption.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="isLocalFileSource" prop="files" class="mk-hide-asterisk">
        <template #label>
          <div class="flex-between w-full">
            <span class="mk-required">{{ t('common.actions.uploadFiles') }}</span>
            <!-- 下载用户导入模板 -->
            <el-button link type="primary" @click="handleDownloadTemplate">{{ t('user.import.downloadTemplate') }}</el-button>
          </div>
        </template>
        <MkDragUpload
          ref="dragUploadRef"
          v-model="importUsersForm.files"
          accept=".xlsx"
          :tip-text="`${t('upload.formats')}: xlsx`"
          @change="handleFileChange"
          @remove="handleFileRemove"
        />
      </el-form-item>

      <el-form-item :label="t('userGroup.title')" prop="userGroupId">
        <el-select
          v-model="importUsersForm.userGroupId"
          class="w-full"
          :loading="userGroupOptionsLoading"
          clearable
          filterable
          :placeholder="t('userGroup.placeholder')"
          fit-input-width
        >
          <el-option v-for="userGroup in userGroupOptions" :key="userGroup.id" :label="userGroup.name" :value="userGroup.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消导入用户 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 导入所选来源的用户 -->
      <el-button type="primary" :loading="importing" :disabled="!canImport" @click="submitImportUsers">{{ t('common.actions.import') }}</el-button>
    </template>
  </MkDialog>
</template>
