<script setup lang="ts">
import { inject, onBeforeUnmount, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem } from '@/api/types'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { MsgError } from '@/utils/message'
import type { McpSetting, McpSource } from '../../types'

defineOptions({ name: 'AiChatNodeMcpSettingDialog' })

const emit = defineEmits<{ submit: [setting: McpSetting]; loaded: [tools: ToolItem[]] }>()
const apiType = inject<string>('apiType', 'workspace')
const store = useWorkflowStore(apiType)

const MCP_SERVER_EXAMPLE = `{
  "math": {
    "url": "https://example.com/sse",
    "transport": "sse"
  }
}`

const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<McpSetting>({ mcp_servers: '', mcp_source: 'referencing', mcp_tool_ids: [] })

// 每次打开刷新包含共享资源的 MCP 工具，关闭或重新打开后忽略旧响应。
const mcpOptions = ref<ToolItem[]>([])
const loading = ref(false)
let requestVersion = 0
function resetData() {
  requestVersion++
  loading.value = false
  mcpOptions.value = []
  formData.value = { mcp_servers: '', mcp_source: 'referencing', mcp_tool_ids: [] }
  formRef.value?.clearValidate()
}
onBeforeUnmount(() => requestVersion++)

function open(setting: McpSetting) {
  resetData()
  formData.value = cloneDeep(setting)
  if (formData.value.mcp_servers) formData.value.mcp_source = 'custom'
  visible.value = true
  const version = ++requestVersion
  loading.value = true
  return store.force
    .getToolListWithShared({ tool_type: TOOL_TYPE.MCP })
    .then((tools) => {
      if (version !== requestVersion || !visible.value) return
      mcpOptions.value = tools
      emit('loaded', tools)
    })
    .finally(() => {
      if (version === requestVersion) loading.value = false
    })
}

function changeSource(source: McpSource) {
  formData.value.mcp_source = source
  if (source === 'custom') formData.value.mcp_tool_ids = []
  else formData.value.mcp_servers = ''
}

function submit() {
  formRef.value?.validate().then(() => {
    if (formData.value.mcp_source === 'custom') {
      try {
        JSON.parse(formData.value.mcp_servers)
      } catch {
        MsgError('MCP 服务配置必须是合法的 JSON')
        return
      }
    }
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="MCP 设置" @closed="resetData">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item>
        <el-radio-group :model-value="formData.mcp_source" @update:model-value="changeSource">
          <el-radio value="referencing">引用 MCP</el-radio>
          <el-radio value="custom">自定义</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="formData.mcp_source === 'referencing'"
        label="MCP 工具"
        prop="mcp_tool_ids"
        :rules="{ type: 'array', required: true, message: '请选择 MCP 工具', trigger: 'change' }"
      >
        <el-select v-model="formData.mcp_tool_ids" class="w-full" :loading="loading" filterable multiple placeholder="请选择 MCP 工具">
          <el-option v-for="option in mcpOptions" :key="option.id" :label="option.name" :value="option.id">
            <div class="flex items-center gap-2">
              <ToolIcon :icon="option.icon" :size="20" :type="option.tool_type" />
              <span>{{ option.name }}</span>
              <el-tag v-if="option.source === 'shared'" size="small" type="info">共享</el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item v-else label="MCP 服务配置" prop="mcp_servers" :rules="{ required: true, message: '请输入 MCP 服务配置', trigger: 'blur' }">
        <el-input v-model="formData.mcp_servers" :placeholder="MCP_SERVER_EXAMPLE" :rows="10" type="textarea" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
