<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import type { ChatUserSyncConflict, ListItem, LoginMethod, RoleType, SystemUserGroup } from '@/api/types'
import { LOGIN_METHOD_LABELS, ROLE_TYPE_LABELS } from '@/constants'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import CurrentUserApi from '@/api/admin/auth/current-user'
import UserManageApi from '@/api/admin/system/user-manage'
import UserGroupApi from '@/api/admin/system/user-groups'
import { useStore } from '@/stores'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'

defineOptions({ name: 'ImportUsersDialog' })

const emit = defineEmits<{ refresh: [] }>()

const { auth } = useStore()

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
  role: RoleType | ''
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
const showWorkspace = computed(() => Boolean(importUsersForm.role) && importUsersForm.role !== ROLE_TYPE.ADMIN)
const showUserGroups = computed(() => importUsersForm.role === ROLE_TYPE.USER)
const canImport = computed(
  () =>
    Boolean(importUsersForm.source) &&
    Boolean(importUsersForm.role) &&
    (!showWorkspace.value || Boolean(importUsersForm.workspaceId)) &&
    (!isLocalFileSource.value || importUsersForm.files.length > 0),
)

const importUsersFormRules: FormRules<ImportUsersForm> = {
  files: [{ required: true, type: 'array', min: 1, message: '请上传文件', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  source: [{ required: true, message: '请选择用户来源', trigger: 'change' }],
  workspaceId: [{ required: true, message: '请选择工作空间', trigger: 'change' }],
}

const roleOptions: RoleType[] = [ROLE_TYPE.USER, ROLE_TYPE.WORKSPACE_MANAGE, ROLE_TYPE.ADMIN]

/* 可导入来源、角色、工作空间与用户组选项 */
const sourcesLoading = ref(false)
const sourceOptions = ref<{ label: string; value: string }[]>([])
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
      sourceOptions.value = [
        ...types.map((source) => ({ label: source === LOGIN_METHOD.LOCAL ? '系统用户' : LOGIN_METHOD_LABELS[source as LoginMethod], value: source })),
        { label: '本地文件', value: LOCAL_FILE_SOURCE },
      ]
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
    })
    .finally(() => {
      rolesLoading.value = false
    })
}

function loadWorkspaceOptions() {
  workspaceLoading.value = true
  if (!auth.isEE) {
    workspaceOptions.value = [{ id: DEFAULT_WORKSPACE_ID, name: '默认工作空间' }]
    importUsersForm.workspaceId ||= DEFAULT_WORKSPACE_ID
    workspaceLoading.value = false
    return Promise.resolve()
  }
  return CurrentUserApi.getCurrentUserWorkspaceList()
    .then((workspaces) => {
      workspaceOptions.value = workspaces
      importUsersForm.workspaceId ||= workspaces[0]?.id || ''
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

watch(
  () => importUsersForm.workspaceId,
  (workspaceId) => {
    if (workspaceId) {
      importUsersForm.userGroupIds = []
      loadUserGroupOptions()
    }
  },
)

/* 导入用户表单联动 */
function handleSourceChange(source: ImportUserSource | '') {
  if (source && !importUsersForm.role) {
    importUsersForm.role = ROLE_TYPE.USER
    importUsersForm.workspaceId = workspaceOptions.value[0]?.id || DEFAULT_WORKSPACE_ID
  }
  if (source !== LOCAL_FILE_SOURCE) {
    importUsersForm.files = []
    dragUploadRef.value?.clearFiles()
  }
  nextTick(() => importUsersFormRef.value?.clearValidate())
}

function handleRoleChange(role: RoleType | '') {
  if (role === ROLE_TYPE.ADMIN) {
    importUsersForm.workspaceId = ''
    importUsersForm.userGroupIds = []
  } else if (role) {
    importUsersForm.workspaceId ||= workspaceOptions.value[0]?.id || DEFAULT_WORKSPACE_ID
    if (role !== ROLE_TYPE.USER) importUsersForm.userGroupIds = []
  }
  nextTick(() => importUsersFormRef.value?.clearValidate(['role', 'workspaceId']))
}

function handleFileChange(file: UploadFile) {
  if (!/\.xlsx$/i.test(file.name)) {
    importUsersForm.files = []
    dragUploadRef.value?.clearFiles()
    MsgWarning('仅支持上传 xlsx 格式的文件')
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

function formatConflictMessage(conflicts: ChatUserSyncConflict[]) {
  return conflicts
    .map((conflict) => {
      const conflictLabel = conflict.type === 'username' ? '用户名已存在' : conflict.type === 'nick_name' ? '姓名已存在' : `${conflict.type} 冲突`
      return `${conflictLabel}：${conflict.users.join('、')}`
    })
    .join('；')
}

function submitImportUsers() {
  if (!importUsersFormRef.value) return

  importUsersFormRef.value.validate((valid) => {
    if (!valid) return

    const syncFile = isLocalFileSource.value ? ((importUsersForm.files[0]?.raw ?? undefined) as File | undefined) : undefined
    const roleId = assignableRoles.value.find((role) => role.type === importUsersForm.role)?.id

    importing.value = true
    return UserManageApi.postSyncSystemUsers(
      isLocalFileSource.value ? 'file' : importUsersForm.source,
      syncFile,
      importUsersForm.workspaceId || undefined,
      roleId,
      importUsersForm.userGroupIds[0],
    )
      .then((result) => {
        const conflictMessage = formatConflictMessage(result.conflict_users ?? [])
        MsgSuccess(`成功导入 ${result.success_count} 个用户${conflictMessage ? `，${conflictMessage}` : ''}`)
        emit('refresh')
        dialogVisible.value = false
      })
      .finally(() => {
        importing.value = false
      })
  })
}

function open() {
  resetData()
  dialogVisible.value = true
  void Promise.all([loadSourceOptions(), loadRoleOptions(), loadWorkspaceOptions()])
}

function resetData() {
  Object.assign(importUsersForm, { files: [], role: '', source: '', userGroupIds: [], workspaceId: '' })
  sourceOptions.value = []
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
  <MkDialog v-model="dialogVisible" title="导入用户" @closed="resetData">
    <template #subtitle>仅导入新增用户</template>

    <el-form
      ref="importUsersFormRef"
      :model="importUsersForm"
      :rules="importUsersFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitImportUsers"
    >
      <el-form-item label="用户来源" prop="source">
        <el-select v-model="importUsersForm.source" placeholder="请选择" :loading="sourcesLoading" @change="handleSourceChange">
          <el-option v-for="sourceOption in sourceOptions" :key="sourceOption.value" :label="sourceOption.label" :value="sourceOption.value" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="isLocalFileSource" prop="files" :required="false">
        <template #label>
          <div class="flex-between w-full">
            <span>上传文件<span class="ml-1 text-danger">*</span></span>
            <el-button link type="primary" @click="handleDownloadTemplate">下载模板</el-button>
          </div>
        </template>
        <MkDragUpload
          ref="dragUploadRef"
          v-model="importUsersForm.files"
          accept=".xlsx"
          tip-text="支持格式：xlsx"
          @change="handleFileChange"
          @remove="handleFileRemove"
        />
      </el-form-item>

      <el-form-item label="角色" prop="role">
        <el-select v-model="importUsersForm.role" placeholder="请选择角色" :loading="rolesLoading" @change="handleRoleChange">
          <el-option v-for="roleOption in roleOptions" :key="roleOption" :label="ROLE_TYPE_LABELS[roleOption]" :value="roleOption" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showWorkspace" label="工作空间" prop="workspaceId">
        <el-select v-model="importUsersForm.workspaceId" :loading="workspaceLoading" placeholder="请选择工作空间">
          <el-option v-for="workspaceOption in workspaceOptions" :key="workspaceOption.id" :label="workspaceOption.name" :value="workspaceOption.id" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showUserGroups" label="用户组" prop="userGroupIds">
        <el-select v-model="importUsersForm.userGroupIds" :loading="userGroupLoading" multiple placeholder="请选择用户组">
          <el-option v-for="userGroupOption in userGroupOptions" :key="userGroupOption.id" :label="userGroupOption.name" :value="userGroupOption.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="importing" :disabled="!canImport" @click="submitImportUsers">导入</el-button>
    </template>
  </MkDialog>
</template>
