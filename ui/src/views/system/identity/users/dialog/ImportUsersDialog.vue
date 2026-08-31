<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import type { RoleType } from '@/api/types'
import { LOGIN_METHOD_LABELS, ROLE_TYPE_LABELS } from '@/constants'
import { MsgInfo, MsgWarning } from '@/utils/message'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'

defineOptions({ name: 'ImportUsersDialog' })

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

const sourceOptions: { label: string; value: ImportUserSource }[] = [
  { label: LOGIN_METHOD_LABELS[LOGIN_METHOD.LDAP], value: LOGIN_METHOD.LDAP },
  { label: LOGIN_METHOD_LABELS[LOGIN_METHOD.WECOM], value: LOGIN_METHOD.WECOM },
  { label: LOGIN_METHOD_LABELS[LOGIN_METHOD.DINGTALK], value: LOGIN_METHOD.DINGTALK },
  { label: LOGIN_METHOD_LABELS[LOGIN_METHOD.LARK], value: LOGIN_METHOD.LARK },
  { label: '本地文件', value: LOCAL_FILE_SOURCE },
]
const roleOptions: RoleType[] = [ROLE_TYPE.USER, ROLE_TYPE.WORKSPACE_MANAGE, ROLE_TYPE.ADMIN]
const workspaceOptions = [
  { label: '默认工作空间', value: DEFAULT_WORKSPACE_ID },
  { label: '研发工作空间', value: 'research-and-development' },
  { label: '营销工作空间', value: 'marketing' },
]
const userGroupOptions = [
  { label: '用户组 1', value: 'user-group-1' },
  { label: '用户组 2', value: 'user-group-2' },
  { label: '产品组', value: 'product-group' },
]

const dialogVisible = ref(false)
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

/* 导入用户表单联动 */
function handleSourceChange(source: ImportUserSource | '') {
  if (source && !importUsersForm.role) {
    importUsersForm.role = ROLE_TYPE.USER
    importUsersForm.workspaceId = DEFAULT_WORKSPACE_ID
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
    importUsersForm.workspaceId ||= DEFAULT_WORKSPACE_ID
    if (role !== ROLE_TYPE.USER) importUsersForm.userGroupIds = []
  }
  nextTick(() => importUsersFormRef.value?.clearValidate(['role', 'workspaceId']))
}

function handleFileChange(file: UploadFile) {
  if (!/\.xlsx?$/i.test(file.name)) {
    importUsersForm.files = []
    dragUploadRef.value?.clearFiles()
    MsgWarning('仅支持上传 xlsx、xls 格式的文件')
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
  MsgInfo('下载模板将在接口接入后提供')
}

function submitImportUsers() {
  if (!importUsersFormRef.value) return

  importUsersFormRef.value.validate((valid) => {
    if (!valid) return
    MsgInfo('导入接口暂未接入')
  })
}

function open() {
  resetData()
  dialogVisible.value = true
}

function resetData() {
  Object.assign(importUsersForm, { files: [], role: '', source: '', userGroupIds: [], workspaceId: '' })
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
        <el-select v-model="importUsersForm.source" placeholder="请选择" @change="handleSourceChange">
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
          accept=".xlsx,.xls"
          tip-text="支持格式：xlsx、xls"
          @change="handleFileChange"
          @remove="handleFileRemove"
        />
      </el-form-item>

      <el-form-item label="角色" prop="role">
        <el-select v-model="importUsersForm.role" placeholder="请选择角色" @change="handleRoleChange">
          <el-option v-for="roleOption in roleOptions" :key="roleOption" :label="ROLE_TYPE_LABELS[roleOption]" :value="roleOption" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showWorkspace" label="工作空间" prop="workspaceId">
        <el-select v-model="importUsersForm.workspaceId" placeholder="请选择工作空间">
          <el-option
            v-for="workspaceOption in workspaceOptions"
            :key="workspaceOption.value"
            :label="workspaceOption.label"
            :value="workspaceOption.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item v-if="showUserGroups" label="用户组" prop="userGroupIds">
        <el-select v-model="importUsersForm.userGroupIds" multiple placeholder="请选择用户组">
          <el-option
            v-for="userGroupOption in userGroupOptions"
            :key="userGroupOption.value"
            :label="userGroupOption.label"
            :value="userGroupOption.value"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :disabled="!canImport" @click="submitImportUsers">导入</el-button>
    </template>
  </MkDialog>
</template>
