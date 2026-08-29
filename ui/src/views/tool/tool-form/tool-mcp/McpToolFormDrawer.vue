<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolPayload } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'McpToolFormDrawer' })

const props = defineProps<{
  api: typeof ToolApi
  folderId: string
  title: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
}>()

interface McpFormModel {
  code: string
  desc: string
  icon: string
  name: string
}

const mcpServerExample = `{
  "math": {
    "url": "https://your-server.example.com/sse",
    "transport": "sse"
  }
}`
const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')
const mcpForm = reactive<McpFormModel>({ code: '', desc: '', icon: '', name: '' })
const formRules: FormRules<McpFormModel> = {
  code: [{ required: true, message: '请输入 MCP Server 配置', trigger: 'blur' }],
  name: [{ required: true, message: '请输入 MCP 名称', trigger: 'blur' }],
}

function isValidConfig() {
  try {
    const config: unknown = JSON.parse(mcpForm.code)
    if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error()
    return true
  } catch {
    MsgError('请输入正确的 MCP Server JSON 配置')
    return false
  }
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid || !isValidConfig()) return

    const payload: ToolPayload = {
      ...cloneDeep(mcpForm),
      tool_type: TOOL_TYPE.MCP,
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

function handleTestConnection() {
  formRef.value?.validateField('code', (valid) => {
    if (!valid || !isValidConfig()) return

    loading.value = true
    props.api
      .postToolTestConnection({ code: mcpForm.code })
      .then(() => MsgSuccess('连接成功'))
      .finally(() => {
        loading.value = false
      })
  })
}

function fillMcpForm(tool: ToolItem) {
  Object.assign(mcpForm, {
    code: tool.code ?? '',
    desc: tool.desc ?? '',
    icon: tool.icon ?? '',
    name: tool.name,
  })
}

function open(tool?: ToolItem) {
  resetData()
  visible.value = true
  originalForm.value = JSON.stringify(mcpForm)
  if (!tool) return

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      if (editId.value !== tool.id || !visible.value) return
      fillMcpForm(toolDetail)
      originalForm.value = JSON.stringify(mcpForm)
    })
    .catch(() => {
      if (editId.value === tool.id) visible.value = false
    })
    .finally(() => {
      if (editId.value === tool.id) formLoading.value = false
    })
}

function handleBeforeClose() {
  if (JSON.stringify(mcpForm) === originalForm.value) {
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
  Object.assign(mcpForm, { code: '', desc: '', icon: '', name: '' })
  editId.value = undefined
  originalForm.value = ''
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
      :model="mcpForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">基本信息</h4>
      <el-form-item label="名称" prop="name">
        <div class="flex w-full items-center gap-3">
          <ToolIcon :icon="mcpForm.icon" :size="32" :type="TOOL_TYPE.MCP" />
          <el-input
            v-model="mcpForm.name"
            maxlength="64"
            placeholder="请输入 MCP 名称"
            show-word-limit
            @blur="mcpForm.name = mcpForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="mcpForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入描述"
          show-word-limit
          type="textarea"
          @blur="mcpForm.desc = mcpForm.desc.trim()"
        />
      </el-form-item>

      <h4 class="mk-title-decoration mk-required mb-4">MCP Server</h4>
      <el-form-item label="MCP Server 配置（JSON）" prop="code">
        <el-input
          v-model="mcpForm.code"
          :autosize="{ minRows: 8 }"
          :placeholder="mcpServerExample"
          type="textarea"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="handleTestConnection">
        测试连接
      </el-button>
      <el-button plain :disabled="loading" @click="handleBeforeClose">取消</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDrawer>
</template>
