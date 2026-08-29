<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolPayload } from '@/api/types'
import { useStore } from '@/stores'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'McpFormDrawer' })

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

interface McpFormModel {
  code: string
  desc: string
  icon: string
  name: string
}

const mcpServerExample = `{
  "math": {
    "url": "your_server",
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
  code: [{ required: true, message: '请输入 MCP Server Config', trigger: 'blur' }],
  name: [{ required: true, message: '请输入 MCP 名称', trigger: 'blur' }],
}

function isValidConfig() {
  try {
    const config: unknown = JSON.parse(mcpForm.code)
    if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error()
    return true
  } catch {
    MsgError('请输入正确的 MCP Server Config')
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

function open(tool?: ToolItem, asCopy = false) {
  resetData()
  visible.value = true
  originalForm.value = JSON.stringify(mcpForm)
  if (!tool) return

  if (asCopy) {
    fillMcpForm(tool)
    originalForm.value = JSON.stringify(mcpForm)
    return
  }

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      fillMcpForm(toolDetail)
      originalForm.value = JSON.stringify(mcpForm)
    })

    .finally(() => {
      formLoading.value = false
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
          <!-- // TODO修改头像 -->
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
          placeholder="请输入"
          show-word-limit
          type="textarea"
          @blur="mcpForm.desc = mcpForm.desc.trim()"
        />
      </el-form-item>

      <h4 class="mk-title-decoration mb-4">MCP 服务</h4>
      <el-form-item prop="code" class="mk-hide-asterisk">
        <template #label>
          <span class="mk-required"> MCP Server Config </span>

          <span class="text-N600"> （仅支持 SSE、Streamable HTTP 调用方式）</span>
        </template>
        <el-input
          v-model="mcpForm.code"
          :autosize="{ minRows: 8 }"
          :placeholder="mcpServerExample"
          type="textarea"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="handleBeforeClose">取消</el-button>
      <el-button plain :disabled="loading || formLoading" @click="handleTestConnection">
        测试连接
      </el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDrawer>
</template>
