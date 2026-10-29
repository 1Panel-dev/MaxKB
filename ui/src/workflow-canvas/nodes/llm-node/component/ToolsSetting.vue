<script setup lang="ts">
import { computed, onBeforeUnmount, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { downloadByURL } from '@/utils/common'
import ToolFunctionDrawer from './ToolFunctionDrawer.vue'
import { normalizeTool, type LlmTool, type LlmToolsSetting } from '../types'

defineOptions({ name: 'WorkflowLlmToolsSetting' })

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()
const setting = defineModel<LlmToolsSetting>({ required: true })

const toolDrawerRef = useTemplateRef<InstanceType<typeof ToolFunctionDrawer>>('toolDrawerRef')
const anchorGuard = createAnchorGuard(props.nodeModel)
const existingNames = computed(() => setting.value.tools.map((tool) => tool.function.name))

function updateSetting(value: Partial<LlmToolsSetting>) {
  setting.value = { ...setting.value, ...value }
}

function handleOpenToolDrawer(tool?: LlmTool, index?: number) {
  toolDrawerRef.value?.open(tool, index)
}

function handleToolSubmit(tool: LlmTool, index?: number) {
  const tools = cloneDeep(setting.value.tools)
  if (index === undefined) tools.push(tool)
  else tools[index] = tool
  updateSetting({ tools })
  toolDrawerRef.value?.close()
}

function handleDeleteTool(index: number) {
  updateSetting({ tools: setting.value.tools.filter((_tool, i) => i !== index) })
}

// 批量导入
const importVisible = ref(false)
const importJson = ref('')
const importError = ref('')

function handleOpenImport() {
  importVisible.value = true
}

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
      工具声明
      <MkTooltip
        content="按 OpenAI 标准 Function Calling 格式声明工具能力，仅用于模型决策，不在此处执行；调用请求（工具名 + 参数）经参数 tool_calls 返回"
        placement="right"
      >
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </span>
    <div class="flex-align-center">
      <template v-if="setting.location === 'customize'">
        <!-- 添加工具 -->
        <el-button text type="primary" @click="handleOpenToolDrawer()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
        <!-- 工具声明更多操作 -->
        <MkDropdown
          class="ml-1"
          :teleported="false"
          trigger="click"
          placement="bottom-end"
          @visible-change="anchorGuard.setOverlayVisible('tools-more', $event)"
        >
          <el-button text type="primary">
            <MkIcon name="icon_more_outlined" />
          </el-button>
          <template #dropdown>
            <MkDropdownMenu>
              <!-- 批量导入工具 -->
              <MkDropdownItem @click="handleOpenImport">
                <template #icon><MkIcon name="icon_import_outlined" /></template>
                导入
              </MkDropdownItem>
              <!-- 导出工具 -->
              <MkDropdownItem :disabled="!setting.tools.length" @click="handleExport">
                <template #icon><MkIcon name="icon_export_outlined" /></template>
                导出
              </MkDropdownItem>
            </MkDropdownMenu>
          </template>
        </MkDropdown>
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
  <MkTable class="border" v-else-if="setting.tools.length" :data="setting.tools" size="small" row-key="function.name" :max-height="undefined">
    <el-table-column label="工具名称">
      <template #default="{ row }">
        <span class="block truncate" :title="row.function.name">{{ row.function.name }}</span>
      </template>
    </el-table-column>
    <el-table-column label="工具描述">
      <template #default="{ row }">
        <span class="block truncate" :title="row.function.description || '-'">{{ row.function.description || '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column label="参数">
      <template #default="{ row }">{{ Object.keys(row.function.parameters?.properties ?? {}).length }}</template>
    </el-table-column>
    <el-table-column label="操作" width="80">
      <template #default="{ row, $index }">
        <!-- 编辑工具 -->
        <el-button text type="primary" @click="handleOpenToolDrawer(row, $index)">
          <MkIcon name="icon_edit_outlined" />
        </el-button>
        <!-- 删除工具 -->
        <el-button text type="primary" @click="handleDeleteTool($index)">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </template>
    </el-table-column>
  </MkTable>

  <ToolFunctionDrawer ref="toolDrawerRef" :existing-names="existingNames" @submit="handleToolSubmit" />

  <MkDialog v-model="importVisible" title="导入工具" @closed="resetImport">
    <el-input
      v-model="importJson"
      type="textarea"
      :rows="12"
      @paste.stop
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
    <div v-if="importError" class="mt-2 text-sm text-danger">{{ importError }}</div>
    <template #footer>
      <el-button plain @click="importVisible = false">取消</el-button>
      <el-button type="primary" @click="handleImport">导入</el-button>
    </template>
  </MkDialog>
</template>
