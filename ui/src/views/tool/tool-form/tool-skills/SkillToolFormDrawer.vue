<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type {
  FormInstance,
  FormRules,
  UploadFile,
  UploadFiles,
  UploadInstance,
  UploadUserFile,
} from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { DynamicFormField, ToolItem, ToolPayload } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import InitFieldTable from '../../components/init-field/InitFieldTable.vue'

defineOptions({ name: 'SkillToolFormDrawer' })

const props = defineProps<{
  api: typeof ToolApi
  folderId: string
  title: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
}>()

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
const uploadRef = useTemplateRef<UploadInstance>('uploadRef')
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')
const skillForm = reactive<SkillFormModel>({
  code: '',
  desc: '',
  fileList: [],
  icon: '',
  init_field_list: [],
  name: '',
})
const formRules: FormRules<SkillFormModel> = {
  fileList: [{ required: true, message: '请上传 Skill ZIP 文件', trigger: 'change' }],
  name: [{ required: true, message: '请输入 Skill 名称', trigger: 'blur' }],
}

function removeUploadFile(file: UploadFile, fileList: UploadFiles) {
  const fileIndex = fileList.findIndex((item) => item.uid === file.uid)
  if (fileIndex >= 0) fileList.splice(fileIndex, 1)
}

function handleFileChange(file: UploadFile, fileList: UploadFiles) {
  if (!file.raw) return
  if (!file.size) {
    MsgError('不能上传空文件')
    removeUploadFile(file, fileList)
    return
  }
  if (file.size / 1024 / 1024 >= maxFileSizeMb) {
    MsgError(`文件大小不能超过 ${maxFileSizeMb} MB`)
    removeUploadFile(file, fileList)
    return
  }

  skillForm.fileList = fileList.slice(-1)
  loading.value = true
  props.api
    .postSkillFile(file.raw)
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
  const fileName = skillForm.fileList[0]?.name || `${skillForm.name}.zip`
  loading.value = true
  props.api.downloadSkillFile(editId.value, fileName).finally(() => {
    loading.value = false
  })
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    const payload: ToolPayload = {
      code: skillForm.code,
      desc: skillForm.desc,
      icon: skillForm.icon,
      init_field_list: cloneDeep(skillForm.init_field_list),
      name: skillForm.name,
      tool_type: TOOL_TYPE.SKILL,
    }
    loading.value = true
    const request = editId.value
      ? props.api.putTool(editId.value, payload)
      : props.api.postTool({ ...payload, folder_id: props.folderId || null })

    request
      .then(() => {
        MsgSuccess(editId.value ? '保存成功' : '创建成功')
        visible.value = false
        emit('refresh')
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

function open(tool?: ToolItem) {
  resetData()
  visible.value = true
  originalForm.value = JSON.stringify(skillForm)
  if (!tool) return

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      if (editId.value !== tool.id || !visible.value) return
      fillSkillForm(toolDetail)
      originalForm.value = JSON.stringify(skillForm)
    })
    .catch(() => {
      if (editId.value === tool.id) visible.value = false
    })
    .finally(() => {
      if (editId.value === tool.id) formLoading.value = false
    })
}

function handleBeforeClose() {
  if (JSON.stringify(skillForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm('提示', '当前的更改尚未保存，确认退出吗？', {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(skillForm, {
    code: '',
    desc: '',
    fileList: [],
    icon: '',
    init_field_list: [],
    name: '',
  })
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

function formatFileSize(size?: number) {
  if (!size) return '0 KB'
  if (size < 1024 * 1024) return `${Math.ceil(size / 1024)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    :before-close="handleBeforeClose"
    :title="title"
    size="60%"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      v-loading="formLoading"
      :model="skillForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">基本信息</h4>
      <el-form-item label="名称" prop="name">
        <div class="flex w-full items-center gap-3">
          <ToolIcon :icon="skillForm.icon" :size="32" :type="TOOL_TYPE.SKILL" />
          <el-input
            v-model="skillForm.name"
            maxlength="64"
            placeholder="请输入 Skill 名称"
            show-word-limit
            @blur="skillForm.name = skillForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="skillForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入描述"
          show-word-limit
          type="textarea"
          @blur="skillForm.desc = skillForm.desc.trim()"
        />
      </el-form-item>

      <InitFieldTable v-model="skillForm.init_field_list" class="mb-6" />

      <section>
        <h4 class="mk-title-decoration mk-required mb-4">Skill 文件</h4>
        <el-form-item prop="fileList">
          <div v-if="skillForm.fileList.length" class="w-full">
            <div class="flex items-center gap-3 rounded-md border border-N200 px-3 py-2">
              <ToolIcon :size="32" :type="TOOL_TYPE.SKILL" />
              <div class="min-w-0 flex-1">
                <p class="truncate" :title="skillForm.fileList[0]?.name">
                  {{ skillForm.fileList[0]?.name }}
                </p>
                <span class="text-sm text-N600">
                  {{ formatFileSize(skillForm.fileList[0]?.size) }}
                </span>
              </div>
            </div>
            <div class="mt-2 flex gap-3">
              <el-upload
                ref="uploadRef"
                v-model:file-list="skillForm.fileList"
                action="#"
                accept=".zip"
                :auto-upload="false"
                :on-change="handleFileChange"
                :show-file-list="false"
              >
                <el-button link type="primary">重新上传</el-button>
              </el-upload>
              <el-button v-if="editId" link type="primary" @click="handleDownload">
                下载
              </el-button>
            </div>
          </div>
          <el-upload
            v-else
            ref="uploadRef"
            v-model:file-list="skillForm.fileList"
            action="#"
            accept=".zip"
            class="w-full"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
          >
            <img src="@/assets/empty/no-data.svg" alt="" />
            <div class="el-upload__text">将 ZIP 文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <span class="text-N600">仅支持 ZIP，文件大小不超过 {{ maxFileSizeMb }} MB</span>
            </template>
          </el-upload>
        </el-form-item>
      </section>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="handleBeforeClose">取消</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDrawer>
</template>
