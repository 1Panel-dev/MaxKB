<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'WorkflowFormDialog' })

const props = defineProps<{
  api: typeof ToolApi
  folderId: string
  title: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
}>()

interface WorkflowFormModel {
  desc: string
  icon: string
  name: string
  work_flow: Record<string, unknown>
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const workflowForm = reactive<WorkflowFormModel>({
  desc: '',
  icon: '',
  name: '',
  work_flow: {},
})
const formRules: FormRules<WorkflowFormModel> = {
  name: [{ required: true, message: '请输入工作流名称', trigger: 'blur' }],
}

function fillWorkflowForm(tool: ToolItem) {
  Object.assign(workflowForm, {
    desc: tool.desc ?? '',
    icon: tool.icon ?? '',
    name: tool.name,
    work_flow: cloneDeep(tool.work_flow ?? {}),
  })
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    const payload: ToolPayload = {
      ...cloneDeep(workflowForm),
      code: 'None',
      tool_type: TOOL_TYPE.WORKFLOW,
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

function open(tool?: ToolItem) {
  resetData()
  visible.value = true
  if (!tool) return

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      if (editId.value === tool.id && visible.value) fillWorkflowForm(toolDetail)
    })
    .catch(() => {
      if (editId.value === tool.id) visible.value = false
    })
    .finally(() => {
      if (editId.value === tool.id) formLoading.value = false
    })
}

function resetData() {
  Object.assign(workflowForm, {
    desc: '',
    icon: '',
    name: '',
    work_flow: {},
  })
  editId.value = undefined
  loading.value = false
  formLoading.value = false
  formRef.value?.clearValidate()
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" append-to-body :title="title" width="550" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="formLoading"
      :model="workflowForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <div class="flex w-full items-center gap-3">
          <ToolIcon :icon="workflowForm.icon" :size="32" :type="TOOL_TYPE.WORKFLOW" />
          <el-input
            v-model="workflowForm.name"
            maxlength="64"
            placeholder="请输入工作流名称"
            show-word-limit
            @blur="workflowForm.name = workflowForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="workflowForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入描述"
          show-word-limit
          type="textarea"
          @blur="workflowForm.desc = workflowForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDialog>
</template>
