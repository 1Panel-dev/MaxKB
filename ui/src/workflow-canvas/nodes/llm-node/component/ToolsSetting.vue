<script setup lang="ts">
import { computed, onBeforeUnmount, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { downloadByURL } from '@/utils/common'
import ToolFunctionDialog from './ToolFunctionDialog.vue'
import { normalizeTool, type LlmTool, type LlmToolsSetting } from '../types'

defineOptions({ name: 'WorkflowLlmToolsSetting' })

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()
const setting = defineModel<LlmToolsSetting>({ required: true })

const toolDialogRef = useTemplateRef<InstanceType<typeof ToolFunctionDialog>>('toolDialogRef')
const anchorGuard = createAnchorGuard(props.nodeModel)
const existingNames = computed(() => setting.value.tools.map((tool) => tool.function.name))

function updateSetting(value: Partial<LlmToolsSetting>) {
  setting.value = { ...setting.value, ...value }
}

function handleToolSubmit(tool: LlmTool, index?: number) {
  const tools = cloneDeep(setting.value.tools)
  if (index === undefined) tools.push(tool)
  else tools[index] = tool
  updateSetting({ tools })
  toolDialogRef.value?.close()
}

function handleDeleteTool(index: number) {
  updateSetting({ tools: setting.value.tools.filter((_tool, i) => i !== index) })
}

// 批量导入
const importVisible = ref(false)
const importJson = ref('')
const importError = ref('')

function handleImport() {
  importError.value = ''
  try {
    const parsed = JSON.parse(importJson.value) as unknown
    const imported = (Array.isArray(parsed) ? parsed : [parsed]).map(normalizeTool).filter((tool) => tool !== null)
    if (!imported.length) {
      importError.value = '未找到有效的工具定义'
      return
    }
    // 同名函数以导入内容覆盖
    const importedNames = new Set(imported.map((tool) => tool.function.name))
    updateSetting({ tools: [...setting.value.tools.filter((tool) => !importedNames.has(tool.function.name)), ...imported] })
    importVisible.value = false
  } catch {
    importError.value = 'JSON 解析失败，请检查格式'
  }
}

function resetImport() {
  importJson.value = ''
  importError.value = ''
}

function handleExport() {
  const blob = new Blob([JSON.stringify(setting.value.tools, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  downloadByURL(url, 'tools.json')
  URL.revokeObjectURL(url)
}

onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <div class="flex-between mb-2">
    <span class="flex-align-center gap-1">
      工具
      <MkTooltip content="OpenAI function 格式的工具定义，只交给模型决策，调用结果从 tool_calls 输出" placement="right">
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </span>
    <div class="flex-align-center">
      <template v-if="setting.location === 'customize'">
        <!-- 批量导入工具 -->
        <MkTooltip content="批量导入" placement="top">
          <el-button text type="primary" @click="importVisible = true">
            <MkIcon name="icon_import_outlined" />
          </el-button>
        </MkTooltip>
        <!-- 导出工具 -->
        <MkTooltip content="导出" placement="top">
          <el-button text type="primary" :disabled="!setting.tools.length" @click="handleExport">
            <MkIcon name="icon_export_outlined" />
          </el-button>
        </MkTooltip>
        <!-- 添加函数 -->
        <el-button text type="primary" @click="toolDialogRef?.open()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </template>
      <el-select
        :model-value="setting.location"
        :teleported="false"
        class="ml-2 w-18!"
        size="small"
        @update:model-value="updateSetting({ location: $event })"
        @visible-change="anchorGuard.setOverlayVisible('tools-location', $event)"
      >
        <el-option label="自定义" value="customize" />
        <el-option label="引用" value="reference" />
      </el-select>
    </div>
  </div>

  <NodeCascader
    v-if="setting.location === 'reference'"
    :model-value="setting.reference"
    :node-model="nodeModel"
    class="w-full!"
    placeholder="请选择工具变量"
    @update:model-value="updateSetting({ reference: $event })"
  />
  <div v-else-if="setting.tools.length" class="mk-white-card space-y-1">
    <div v-for="(tool, index) in setting.tools" :key="tool.function.name" class="flex-between gap-2">
      <div class="flex-align-center min-w-0 gap-1">
        <span class="truncate" :title="tool.function.name">{{ tool.function.name }}</span>
        <MkTooltip v-if="tool.function.description" :content="tool.function.description" effect="dark" placement="right">
          <MkIcon name="icon_info_outlined" class="text-N600!" />
        </MkTooltip>
        <el-tag size="small" type="info">{{ Object.keys(tool.function.parameters?.properties ?? {}).length }} 个参数</el-tag>
      </div>
      <div class="flex-align-center shrink-0">
        <!-- 编辑函数 -->
        <el-button text type="primary" @click="toolDialogRef?.open(tool, index)">
          <MkIcon name="icon_edit_outlined" />
        </el-button>
        <!-- 删除函数 -->
        <el-button text type="primary" @click="handleDeleteTool(index)">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </div>
    </div>
  </div>

  <ToolFunctionDialog ref="toolDialogRef" :existing-names="existingNames" @submit="handleToolSubmit" />

  <MkDialog v-model="importVisible" title="批量导入工具" @closed="resetImport">
    <el-input
      v-model="importJson"
      type="textarea"
      :rows="12"
      placeholder='粘贴 OpenAI tools 格式 JSON，例如：
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "获取天气",
      "parameters": {
        "type": "object",
        "properties": { "location": { "type": "string", "description": "城市" } },
        "required": ["location"]
      }
    }
  }
]'
    />
    <div v-if="importError" class="mt-2 text-sm text-[var(--el-color-danger)]">{{ importError }}</div>
    <template #footer>
      <el-button plain @click="importVisible = false">取消</el-button>
      <el-button type="primary" @click="handleImport">导入</el-button>
    </template>
  </MkDialog>
</template>
