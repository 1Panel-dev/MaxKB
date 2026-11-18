<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { DynamicFormField, ToolItem, ToolPayload } from '@/api/types'
import type { FormInstance, FormRules, UploadFile, UploadFiles, UploadUserFile } from 'element-plus'
import { FILE_SOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import InitFieldTable from './component/init-field/InitFieldTable.vue'
import { useStore } from '@/stores'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SkillToolFormDrawer' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; folderId: string; title: string }>()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface SkillFormModel {
  code: string
  desc: string
  fileList: UploadUserFile[]
  icon: string
  init_field_list: DynamicFormField[]
  name: string
}

const maxFileSizeMb = 100
const formRef = ref<FormInstance>()
const uploadRef = useTemplateRef<InstanceType<typeof MkDragUpload>>('uploadRef')
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')
const skillForm = reactive<SkillFormModel>({ code: '', desc: '', fileList: [], icon: '', init_field_list: [], name: '' })
const formRules = computed<FormRules<SkillFormModel>>(() => ({
  fileList: [{ required: true, message: t('tool.skill.file.requiredMessage'), trigger: 'change' }],
  name: [{ whitespace: true, required: true, message: t('tool.skill.name.requiredMessage'), trigger: 'blur' }],
}))

// 暂存确认后的头像文件，恢复默认时清空。
const iconFile = ref<File | null>(null)
function handleIconChange(file: File | null) {
  iconFile.value = file
}

function removeUploadFile(file: UploadFile, fileList: UploadFiles) {
  const fileIndex = fileList.findIndex((item) => item.uid === file.uid)
  if (fileIndex >= 0) fileList.splice(fileIndex, 1)
}

function handleFileChange(file: UploadFile, fileList: UploadFiles) {
  if (!file.raw) return
  if (!file.size) {
    MsgError(t('common.upload.emptyFileMessage'))
    removeUploadFile(file, fileList)
    return
  }
  if (file.size / 1024 / 1024 >= maxFileSizeMb) {
    MsgError(t('tool.skill.file.sizeLimitMessage', { size: maxFileSizeMb }))
    removeUploadFile(file, fileList)
    return
  }

  skillForm.fileList = fileList.slice(-1)
  loading.value = true
  props.api
    .putUploadSkillFile(file.raw)
    .then((fileId) => {
      skillForm.code = fileId
      formRef.value?.validateField('fileList').catch(() => {})
    })
    .catch(() => {
      skillForm.fileList = []
      uploadRef.value?.clearFiles()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDownload() {
  if (!editId.value) return

  loading.value = true
  props.api.downloadSkillFile(editId.value).finally(() => {
    loading.value = false
  })
}

function handleRemoveFile() {
  skillForm.code = ''
  formRef.value?.validateField('fileList').catch(() => {})
}

function handleSubmit() {
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value) return

    loading.value = true
    const currentEditId = editId.value
    const isEdit = Boolean(currentEditId)
    // 新头像先上传并替换预览地址，再提交完整工具表单。
    const uploadIcon = iconFile.value
      ? FileApi.postUploadFile(iconFile.value, currentEditId, FILE_SOURCE_TYPE.TOOL).request.then((icon) => {
          skillForm.icon = icon
          iconFile.value = null
        })
      : Promise.resolve()

    return uploadIcon
      .then(() => {
        const payload: ToolPayload = {
          code: skillForm.code,
          desc: skillForm.desc,
          icon: skillForm.icon,
          init_field_list: cloneDeep(skillForm.init_field_list),
          name: skillForm.name,
          tool_type: TOOL_TYPE.SKILL,
        }
        const request = currentEditId
          ? props.api.putTool(currentEditId, payload)
          : 'postTool' in props.api
            ? props.api.postTool({ ...payload, folder_id: props.folderId || null })
            : Promise.reject(new Error(t('tool.messages.createUnsupported')))

        return request.then((savedTool) => {
          const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
          return refreshCurrentUser.then(() => {
            MsgSuccess(isEdit ? t('common.messages.saveSuccess') : t('common.messages.createSuccess'))
            visible.value = false
            if (isEdit) emit('update', savedTool)
            else emit('refresh')
          })
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function fillSkillForm(tool: ToolItem) {
  Object.assign(skillForm, {
    code: tool.code ?? '',
    desc: tool.desc ?? '',
    fileList: cloneDeep(tool.fileList ?? []),
    icon: tool.icon ?? '',
    init_field_list: cloneDeep(tool.init_field_list ?? []),
    name: tool.name,
  })
}

function open(tool?: ToolItem, asCopy = false) {
  visible.value = true
  originalForm.value = JSON.stringify(skillForm)
  if (!tool) return

  if (asCopy) {
    fillSkillForm(tool)
    originalForm.value = JSON.stringify(skillForm)
    return
  }

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      fillSkillForm(toolDetail)
      originalForm.value = JSON.stringify(skillForm)
    })

    .finally(() => {
      formLoading.value = false
    })
}

function handleBeforeClose() {
  if (loading.value) return
  if (JSON.stringify(skillForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm(t('common.dialogs.notice'), `${t('common.dialogs.unsavedChanges')}?`, {
    confirmButtonText: t('common.actions.confirm'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(skillForm, { code: '', desc: '', fileList: [], icon: '', init_field_list: [], name: '' })
  iconFile.value = null
  editId.value = undefined
  originalForm.value = ''
  loading.value = false
  formLoading.value = false
  uploadRef.value?.clearFiles()
  formRef.value?.clearValidate()
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :before-close="handleBeforeClose" :title="title" size="60%" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="formLoading || loading"
      :model="skillForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">{{ t('common.labels.basicInfo') }}</h4>
      <el-form-item class="mk-form-item-with-avatar" :label="t('common.name.label')" prop="name">
        <div class="flex-align-center w-full gap-3">
          <!-- 设置工具头像 -->
          <MkEditAvatar v-model="skillForm.icon" @change="handleIconChange">
            <template #default="{ icon }">
              <ToolIcon :icon="icon" :type="TOOL_TYPE.SKILL" />
            </template>
          </MkEditAvatar>
          <el-input
            v-model="skillForm.name"
            maxlength="64"
            :placeholder="t('tool.skill.name.placeholder')"
            show-word-limit
            @blur="skillForm.name = skillForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="skillForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          :placeholder="t('common.placeholders.input')"
          show-word-limit
          type="textarea"
          @blur="skillForm.desc = skillForm.desc.trim()"
        />
      </el-form-item>

      <InitFieldTable v-model="skillForm.init_field_list" class="mb-6" />

      <section>
        <h4 class="mk-title-decoration mk-required mb-4">{{ t('tool.skill.file.label') }}</h4>
        <el-form-item prop="fileList">
          <MkDragUpload
            ref="uploadRef"
            v-model="skillForm.fileList"
            accept=".zip"
            :drag-text="t('common.upload.dropHint')"
            :select-text="t('common.upload.selectFile')"
            :replace-text="t('common.upload.replaceFile')"
            :tip-text="t('tool.skill.file.description', { size: maxFileSizeMb })"
            @change="handleFileChange"
            @remove="handleRemoveFile"
          >
            <template #download>
              <!-- 下载 Skill 文件 -->
              <el-button v-if="editId" :disabled="loading" text @click="handleDownload">
                <MkIcon name="icon_download_outlined" class="text-N600" />
              </el-button>
            </template>
          </MkDragUpload>
        </el-form-item>
      </section>
    </el-form>

    <template #footer>
      <!-- 取消编辑 -->
      <el-button plain :disabled="loading || formLoading" @click="handleBeforeClose">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存或创建 Skill -->
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDrawer>
</template>
