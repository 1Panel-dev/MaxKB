<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { MsgError } from '@/utils/message'
import type { McpSetting, McpSource, ToolResourceOption } from '../../types'

defineOptions({ name: 'AiChatNodeMcpSettingDialog' })

defineProps<{ options: ToolResourceOption[] }>()
const emit = defineEmits<{ submit: [setting: McpSetting] }>()

const MCP_SERVER_EXAMPLE = `{
  "math": {
    "url": "https://example.com/sse",
    "transport": "sse"
  }
}`

const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<McpSetting>({ mcp_servers: '', mcp_source: 'referencing', mcp_tool_ids: [] })

function open(setting: McpSetting) {
  formData.value = cloneDeep(setting)
  if (formData.value.mcp_servers) formData.value.mcp_source = 'custom'
  visible.value = true
  nextTick(() => formRef.value?.clearValidate())
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
  <MkDialog v-model="visible" title="MCP 设置" width="600">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item>
        <el-radio-group :model-value="formData.mcp_source" @update:model-value="changeSource">
          <el-radio value="referencing">引用 MCP 工具</el-radio>
          <el-radio value="custom">自定义 MCP 服务</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="formData.mcp_source === 'referencing'"
        label="MCP 工具"
        prop="mcp_tool_ids"
        :rules="{ type: 'array', required: true, message: '请选择 MCP 工具', trigger: 'change' }"
      >
        <el-select v-model="formData.mcp_tool_ids" class="w-full" filterable multiple placeholder="请选择 MCP 工具">
          <el-option v-for="option in options" :key="option.id" :label="option.name" :value="option.id">
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
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
