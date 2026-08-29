<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { Download } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile, UploadFiles, UploadUserFile } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { DynamicFormField, ToolItem, ToolPayload } from '@/api/types'
import MkDragUpload from '@/components/mk-drag-upload/index.vue'
import { useStore } from '@/stores'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

import InitFieldTable from '../components/init-field/InitFieldTable.vue'

defineOptions({ name: 'SkillToolFormDrawer' })

const { auth } = useStore()

const props = defineProps<{
  api: typeof ToolApi
  folderId: string
  title: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
  update: [tool: ToolItem]
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
const uploadRef = useTemplateRef<InstanceType<typeof MkDragUpload>>('uploadRef')
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
    const currentEditId = editId.value
    const isEdit = Boolean(currentEditId)
    const request = currentEditId
      ? props.api.putTool(currentEditId, payload)
      : props.api.postTool({ ...payload, folder_id: props.folderId || null })

    request
      .then((savedTool) => {
        const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
        return refreshCurrentUser.then(() => {
          MsgSuccess(isEdit ? '保存成功' : '创建成功')
          visible.value = false
          if (isEdit) emit('update', savedTool)
          else emit('refresh')
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
  resetData()
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
          <!-- // TODO 头像修改 -->
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
          placeholder="请输入"
          show-word-limit
          type="textarea"
          @blur="skillForm.desc = skillForm.desc.trim()"
        />
      </el-form-item>

      <InitFieldTable v-model="skillForm.init_field_list" class="mb-6" />

      <section>
        <h4 class="mk-title-decoration mk-required mb-4">Skill 文件</h4>
        <el-form-item prop="fileList">
          <MkDragUpload
            ref="uploadRef"
            v-model="skillForm.fileList"
            accept=".zip"
            :disabled="loading"
            :tip-text="`支持格式：ZIP，大小不超过 ${maxFileSizeMb} MB`"
            @change="handleFileChange"
            @remove="handleRemoveFile"
          >
            <template #download>
              <el-button v-if="editId" :disabled="loading" link @click="handleDownload">
                <MkIcon :icon="Download" :size="16" class="text-N600" />
              </el-button>
            </template>
          </MkDragUpload>
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
