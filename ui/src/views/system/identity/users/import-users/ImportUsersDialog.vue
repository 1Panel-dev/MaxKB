<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUserSyncConflict, ListItem, LoginMethod, SystemUserGroup } from '@/api/types'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserGroupApi from '@/api/admin/system/user-groups'
import UserManageApi from '@/api/admin/system/user-manage'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { useStore } from '@/stores'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ImportUsersDialog' })

const emit = defineEmits<{ refresh: [] }>()

const { auth } = useStore()
const { t } = useI18n({ useScope: 'global' })

const LOCAL_FILE_SOURCE = 'LOCAL_FILE' as const
const DEFAULT_WORKSPACE_ID = 'default'

type ImportUserSource =
  | typeof LOGIN_METHOD.LDAP
  | typeof LOGIN_METHOD.WECOM
  | typeof LOGIN_METHOD.DINGTALK
  | typeof LOGIN_METHOD.LARK
  | typeof LOCAL_FILE_SOURCE

interface ImportUsersForm {
  files: UploadUserFile[]
  role: string
  source: ImportUserSource | ''
  userGroupIds: string[]
  workspaceId: string
}

const dialogVisible = ref(false)
const importing = ref(false)
const importUsersFormRef = ref<FormInstance>()
const dragUploadRef = ref<InstanceType<typeof MkDragUpload>>()
const importUsersForm = reactive<ImportUsersForm>({ files: [], role: '', source: '', userGroupIds: [], workspaceId: '' })
const isLocalFileSource = computed(() => importUsersForm.source === LOCAL_FILE_SOURCE)
const selectedRoleType = computed(() => assignableRoles.value.find((role) => role.id === importUsersForm.role)?.type)
const showWorkspace = computed(() => Boolean(importUsersForm.role) && selectedRoleType.value !== ROLE_TYPE.ADMIN)
const showUserGroups = computed(() => selectedRoleType.value === ROLE_TYPE.USER)
const canImport = computed(
  () =>
    Boolean(importUsersForm.source) &&
    Boolean(importUsersForm.role) &&
    (!showWorkspace.value || Boolean(importUsersForm.workspaceId)) &&
    (!isLocalFileSource.value || importUsersForm.files.length > 0),
)

const importUsersFormRules = computed<FormRules<ImportUsersForm>>(() => ({
  files: [{ required: true, type: 'array', min: 1, message: t('upload.requiredMessage'), trigger: 'change' }],
  role: [{ required: true, message: t('user.role.requiredMessage'), trigger: 'change' }],
  source: [{ required: true, message: t('user.source.requiredMessage'), trigger: 'change' }],
  workspaceId: [{ required: true, message: t('user.workspace.requiredMessage'), trigger: 'change' }],
}))

/* 可导入来源、角色、工作空间与用户组选项 */
const sourcesLoading = ref(false)
const sourceTypes = ref<string[]>([])
const userSourceLabels = computed<Record<LoginMethod | typeof LOCAL_FILE_SOURCE, string>>(() => ({
  ...LOGIN_METHOD_LABELS,
  [LOGIN_METHOD.LOCAL]: t('user.source.local'),
  [LOGIN_METHOD.DINGTALK]: t('auth.login.options.dingtalk'),
  [LOGIN_METHOD.LARK]: t('auth.login.options.lark'),
  [LOGIN_METHOD.WECOM]: t('auth.login.options.wecom'),
  [LOCAL_FILE_SOURCE]: t('user.source.localFile'),
}))
const sourceOptions = computed(() =>
  sourceTypes.value.map((source) => ({ label: userSourceLabels.value[source as keyof typeof userSourceLabels.value] ?? source, value: source })),
)
const rolesLoading = ref(false)
const assignableRoles = ref<ListItem[]>([])
const workspaceLoading = ref(false)
const workspaceOptions = ref<ListItem[]>([])
const userGroupLoading = ref(false)
const userGroupOptions = ref<SystemUserGroup[]>([])

function loadSourceOptions() {
  sourcesLoading.value = true
  return UserManageApi.getUserManageSyncTypes()
    .then((types) => {
      sourceTypes.value = [...types, LOCAL_FILE_SOURCE]
      importUsersForm.source = (sourceOptions.value[0]?.value as ImportUserSource) || ''
    })
    .finally(() => {
      sourcesLoading.value = false
    })
}

function loadRoleOptions() {
  rolesLoading.value = true
  return CurrentUserApi.getCurrentUserRoleList()
    .then((roles) => {
      assignableRoles.value = roles
      if (!importUsersForm.role) {
        importUsersForm.role = roles.find((role) => role.type === ROLE_TYPE.USER)?.id || ''
      }
    })
    .finally(() => {
      rolesLoading.value = false
    })
}

function loadWorkspaceOptions() {
  workspaceLoading.value = true
  if (!auth.isEE) {
    workspaceOptions.value = [{ id: DEFAULT_WORKSPACE_ID, name: t('workspace.default') }]
    handleWorkspaceChange(importUsersForm.workspaceId || DEFAULT_WORKSPACE_ID)
    workspaceLoading.value = false
    return Promise.resolve()
  }
  return CurrentUserApi.getCurrentUserWorkspaceList()
    .then((workspaces) => {
      workspaceOptions.value = workspaces
      handleWorkspaceChange(importUsersForm.workspaceId || workspaces[0]?.id || '')
    })
    .finally(() => {
      workspaceLoading.value = false
    })
}

function loadUserGroupOptions() {
  if (!importUsersForm.workspaceId) {
    userGroupOptions.value = []
    return
  }
  userGroupLoading.value = true
  return UserGroupApi.getSystemUserGroups(importUsersForm.workspaceId)
    .then((groups) => {
      userGroupOptions.value = groups
    })
    .finally(() => {
      userGroupLoading.value = false
    })
}

/* 导入用户表单联动 */
function handleWorkspaceChange(workspaceId: string) {
  if (workspaceId === importUsersForm.workspaceId) return
  importUsersForm.workspaceId = workspaceId
  importUsersForm.userGroupIds = []
  userGroupOptions.value = []
  void loadUserGroupOptions()
}

function handleSourceChange(source: ImportUserSource | '') {
  if (source && !importUsersForm.role) {
    importUsersForm.role = ROLE_TYPE.USER
    handleWorkspaceChange(workspaceOptions.value[0]?.id || DEFAULT_WORKSPACE_ID)
  }
  if (source !== LOCAL_FILE_SOURCE) {
    importUsersForm.files = []
    dragUploadRef.value?.clearFiles()
  }
  nextTick(() => importUsersFormRef.value?.clearValidate())
}

function handleRoleChange(role: string) {
  if (role === '') {
    importUsersForm.workspaceId = ''
    importUsersForm.userGroupIds = []
  } else if (selectedRoleType.value === ROLE_TYPE.ADMIN) {
    handleWorkspaceChange('')
    importUsersForm.userGroupIds = []
  } else {
    handleWorkspaceChange(importUsersForm.workspaceId || workspaceOptions.value[0]?.id || DEFAULT_WORKSPACE_ID)
    if (selectedRoleType.value !== ROLE_TYPE.USER) importUsersForm.userGroupIds = []
  }
  nextTick(() => importUsersFormRef.value?.clearValidate(['role', 'workspaceId']))
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

function handleDownloadTemplate() {
  UserManageApi.getUserManageImportTemplate()
}

function conflictTypeLabel(type: ChatUserSyncConflict['type']) {
  if (type === 'username') return t('user.username.existsMessage')
  if (type === 'email') return t('user.email.existsMessage')
  if (type === 'nick_name') return t('user.name.existsMessage')
  return t('user.import.conflictMessage', { type })
}

function formatConflictMessage(conflicts: ChatUserSyncConflict[]) {
  return conflicts.map((conflict) => `${conflictTypeLabel(conflict.type)}：${conflict.users.join('、')}`).join('；')
}

function submitImportUsers() {
  if (!importUsersFormRef.value) return

  importUsersFormRef.value.validate((valid) => {
    if (!valid) return

    const syncFile = isLocalFileSource.value ? ((importUsersForm.files[0]?.raw ?? undefined) as File | undefined) : undefined
    importing.value = true
    return UserManageApi.postSyncSystemUsers(
      isLocalFileSource.value ? 'file' : importUsersForm.source,
      syncFile,
      importUsersForm.workspaceId || undefined,
      importUsersForm.role,
      importUsersForm.userGroupIds,
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
  void Promise.all([loadSourceOptions(), loadRoleOptions(), loadWorkspaceOptions()])
}

function resetData() {
  Object.assign(importUsersForm, { files: [], role: '', source: '', userGroupIds: [], workspaceId: '' })
  sourceTypes.value = []
  assignableRoles.value = []
  workspaceOptions.value = []
  userGroupOptions.value = []
  sourcesLoading.value = false
  rolesLoading.value = false
  workspaceLoading.value = false
  userGroupLoading.value = false
  importing.value = false
  dragUploadRef.value?.clearFiles()
  importUsersFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('user.import.title')" @closed="resetData">
    <template #subtitle>{{ t('user.import.onlyNewHint') }}</template>

    <el-form
      ref="importUsersFormRef"
      :model="importUsersForm"
      :rules="importUsersFormRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitImportUsers"
    >
      <el-form-item :label="t('user.source.label')" prop="source">
        <el-select
          v-model="importUsersForm.source"
          :placeholder="t('common.placeholders.select')"
          :loading="sourcesLoading"
          @change="handleSourceChange"
        >
          <el-option v-for="sourceOption in sourceOptions" :key="sourceOption.value" :label="sourceOption.label" :value="sourceOption.value" />
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

      <el-form-item :label="t('user.role.label')" prop="role">
        <el-select v-model="importUsersForm.role" :placeholder="t('user.role.placeholder')" :loading="rolesLoading" @change="handleRoleChange">
          <el-option
            v-for="roleOption in assignableRoles"
            :key="roleOption.id"
            :label="roleOption.name"
            :title="roleOption.name"
            :value="roleOption.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showWorkspace" :label="t('workspace.title')" prop="workspaceId">
        <el-select
          :model-value="importUsersForm.workspaceId"
          :loading="workspaceLoading"
          :placeholder="t('user.workspace.placeholder')"
          @change="handleWorkspaceChange"
        >
          <el-option
            v-for="workspaceOption in workspaceOptions"
            :key="workspaceOption.id"
            :label="!auth.isEE && workspaceOption.id === DEFAULT_WORKSPACE_ID ? t('workspace.default') : workspaceOption.name"
            :value="workspaceOption.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showUserGroups" :label="t('userGroup.title')" prop="userGroupIds">
        <el-select v-model="importUsersForm.userGroupIds" :loading="userGroupLoading" multiple :placeholder="t('userGroup.placeholder')">
          <el-option
            v-for="userGroupOption in userGroupOptions"
            :key="userGroupOption.id"
            :label="userGroupOption.name"
            :value="userGroupOption.id"
          />
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
