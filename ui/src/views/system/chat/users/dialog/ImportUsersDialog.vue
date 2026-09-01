<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import ChatUserApi from '@/api/admin/system/chat-user/chat-user'
import ChatUserGroupsApi from '@/api/admin/system/chat-user/chat-user-groups'
import UserManageApi from '@/api/admin/system/user-manage'
import type { ChatUserSyncConflict, ListItem, OptionItem, LoginMethod } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'

defineOptions({ name: 'ImportUsersDialog' })

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
const syncTypeOptions = ref<OptionItem<string>[]>([])
const importUsersForm = reactive<ImportUsersForm>({ files: [], syncType: '', userGroupId: '' })
const importUsersFormRules: FormRules<ImportUsersForm> = {
  files: [{ required: true, type: 'array', min: 1, message: '请上传文件', trigger: 'change' }],
  syncType: [{ required: true, message: '请选择用户来源', trigger: 'change' }],
}
const isLocalFileSource = computed(() => importUsersForm.syncType === LOCAL_FILE_SOURCE)
const canImport = computed(() => Boolean(importUsersForm.syncType) && (!isLocalFileSource.value || importUsersForm.files.length > 0))

/* 获取导入用户的来源类型 */
const syncTypesLoading = ref(false)
function loadSyncTypes() {
  syncTypesLoading.value = true
  return ChatUserApi.getChatUserSyncTypes()
    .then((syncTypes) => {
      syncTypeOptions.value = [
        ...syncTypes.map((syncType) => ({ label: syncType === LOGIN_METHOD.LOCAL ? '系统用户' : LOGIN_METHOD_LABELS[syncType as LoginMethod], value: syncType })),
        { label: '本地文件', value: LOCAL_FILE_SOURCE },
      ]
      importUsersForm.syncType = syncTypeOptions.value[0]?.value ?? ''
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

function formatConflictMessage(conflicts: ChatUserSyncConflict[]) {
  return conflicts
    .map((conflict) => {
      const conflictLabel = conflict.type === 'username' ? '用户名已存在' : conflict.type === 'nick_name' ? '姓名已存在' : `${conflict.type} 冲突`
      return `${conflictLabel}：${conflict.users.join('、')}`
    })
    .join('；')
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
    return ChatUserApi.postSyncChatUsers(isLocalFileSource.value ? 'file' : importUsersForm.syncType, importUsersForm.userGroupId || undefined, syncFile)
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
  dialogVisible.value = true
  loadSyncTypes()
  loadUserGroupOptions()
}

function resetData() {
  Object.assign(importUsersForm, { files: [], syncType: '', userGroupId: '' })
  syncTypeOptions.value = []
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
  <MkDialog v-model="dialogVisible" title="导入用户" @closed="resetData">
    <template #subtitle> 从已配置的用户来源同步对话用户，已存在的用户名或姓名不会重复导入。 </template>

    <el-form
      ref="importUsersFormRef"
      :model="importUsersForm"
      :rules="importUsersFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submitImportUsers"
    >
      <el-form-item label="用户来源" prop="syncType">
        <el-select v-model="importUsersForm.syncType" class="w-full" :loading="syncTypesLoading" placeholder="请选择用户来源">
          <el-option v-for="syncTypeOption in syncTypeOptions" :key="syncTypeOption.value" :label="syncTypeOption.label" :value="syncTypeOption.value" />
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

      <el-form-item label="用户组">
        <el-select v-model="importUsersForm.userGroupId" class="w-full" :loading="userGroupOptionsLoading" clearable filterable placeholder="请选择用户组" fit-input-width>
          <el-option v-for="userGroup in userGroupOptions" :key="userGroup.id" :label="userGroup.name" :value="userGroup.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="importing" :disabled="!canImport" @click="submitImportUsers">导入</el-button>
    </template>
  </MkDialog>
</template>
