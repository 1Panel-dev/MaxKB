<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { McpSetting, McpSource } from '../../types'
import type { ToolItem } from '@/api/types'
import type { FormInstance } from 'element-plus'
import type { Ref } from 'vue'
import { TOOL_SCOPE, TOOL_TYPE } from '@/api/enums'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'AiChatNodeMcpSettingDialog' })
const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [setting: McpSetting]; loaded: [tools: ToolItem[]] }>()
const resourceScope = inject<string>('resourceScope', 'workspace')
const resourceWorkspaceId = inject<Ref<string | null | undefined>>('resourceWorkspaceId', ref())
const store = useWorkflowStore(resourceScope, () => resourceWorkspaceId.value)

const MCP_SERVER_EXAMPLE = `{
  "math": {
    "url": "https://example.com/sse",
    "transport": "sse"
  }
}`

const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<McpSetting>({ mcp_servers: '', mcp_source: 'referencing', mcp_tool_ids: [] })

// 每次打开刷新包含共享资源的 MCP 工具。
const mcpOptions = ref<ToolItem[]>([])
const loading = ref(false)

// 接口可能返回对象配置；空对象表示未配置，非空对象转为 JSON 文本供输入框编辑。
function normalizeMcpServers(value: unknown): string {
  if (value == null) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 0) return ''
  return JSON.stringify(value, null, 2) ?? ''
}

function open(setting: McpSetting) {
  formData.value = cloneDeep(setting)
  formData.value.mcp_servers = normalizeMcpServers(setting.mcp_servers)
  if (formData.value.mcp_servers) formData.value.mcp_source = 'custom'
  visible.value = true

  loading.value = true
  return store.force
    .getToolListWithShared({ tool_type: TOOL_TYPE.MCP })
    .then((tools) => {
      if (!visible.value) return
      mcpOptions.value = tools.filter((item) => item.is_active)
      emit('loaded', tools)
    })
    .finally(() => {
      loading.value = false
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
        MsgError(t('tool.mcp.config.invalidJsonMessage'))
        return
      }
    }
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

function resetData() {
  loading.value = false
  mcpOptions.value = []
  formData.value = { mcp_servers: '', mcp_source: 'referencing', mcp_tool_ids: [] }
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('tool.mcp.settingsTitle')" @closed="resetData">
    <el-form ref="formRef" :model="formData" :validate-on-rule-change="false" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item>
        <el-radio-group :model-value="formData.mcp_source" @update:model-value="changeSource">
          <el-radio value="referencing">{{ t('common.options.reference') }} MCP</el-radio>
          <el-radio value="custom">{{ t('common.options.custom') }}</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="formData.mcp_source === 'referencing'"
        :label="t('tool.mcp.tools.label')"
        prop="mcp_tool_ids"
        :rules="{ type: 'array', required: true, message: t('tool.mcp.tools.requiredMessage'), trigger: 'change' }"
      >
        <el-select
          v-model="formData.mcp_tool_ids"
          class="w-full"
          :loading="loading"
          filterable
          multiple
          :placeholder="t('tool.mcp.tools.placeholder')"
        >
          <el-option v-for="option in mcpOptions" :key="option.id" :label="option.name" :value="option.id">
            <div class="flex-align-center gap-2">
              <ToolIcon :icon="option.icon" :size="20" :type="option.tool_type" />
              <span class="min-w-0 truncate" :title="option.name">{{ option.name }}</span>
              <el-tag v-if="option.scope === TOOL_SCOPE.SHARED" size="small" type="info">{{ t('resource.shared') }}</el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item
        v-else
        class="mk-hide-asterisk"
        prop="mcp_servers"
        :rules="{ whitespace: true, required: true, message: t('tool.mcp.config.requiredMessage'), trigger: 'blur' }"
      >
        <template #label>
          <span class="mk-required">{{ t('resource.mcpConfig.title') }}</span>
          <span class="text-N600">（{{ t('tool.mcp.config.description') }}）</span>
        </template>
        <el-input v-model="formData.mcp_servers" :placeholder="MCP_SERVER_EXAMPLE" :rows="10" type="textarea" />
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消 MCP 设置 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确定 MCP 设置 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.comfirm') }}</el-button>
    </template>
  </MkDialog>
</template>
