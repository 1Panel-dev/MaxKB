<script setup lang="ts">
import { computed, onBeforeUnmount, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { LlmTool, LlmToolsSetting } from '../types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormItemRule } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'
import ToolFunctionDrawer from './ToolFunctionDrawer.vue'
import ToolImportDialog from './ToolImportDialog.vue'
import { downloadByURL } from '@/utils/common'

defineOptions({ name: 'WorkflowLlmToolsSetting' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ nodeModel: WorkflowNodeModel }>()
const setting = defineModel<LlmToolsSetting>({ required: true })

const toolDrawerRef = useTemplateRef<InstanceType<typeof ToolFunctionDrawer>>('toolDrawerRef')
const toolImportDialogRef = useTemplateRef<InstanceType<typeof ToolImportDialog>>('toolImportDialogRef')
const referenceCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('referenceCascaderRef')
const anchorGuard = createAnchorGuard(props.nodeModel)
const existingNames = computed(() => setting.value.tools.map((tool) => tool.function.name))

// 表单项仅在引用来源时渲染，切回自定义后随表单项卸载移出外层表单校验。
const referenceRules: FormItemRule[] = [
  { type: 'array', required: true, message: t('workflow.referenceVariable.requiredMessage'), trigger: 'change' },
  { asyncValidator: () => referenceCascaderRef.value?.validate() ?? Promise.resolve(), trigger: 'change' },
]

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

function handleOpenImport() {
  toolImportDialogRef.value?.open()
}

function handleImport(imported: LlmTool[]) {
  // 同名函数以导入内容覆盖
  const importedNames = new Set(imported.map((tool) => tool.function.name))
  updateSetting({ tools: [...setting.value.tools.filter((tool) => !importedNames.has(tool.function.name)), ...imported] })
  toolImportDialogRef.value?.close()
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
      {{ t('workflow.llm.tools.label') }}
      <MkTooltip :content="t('workflow.llm.tools.description')" placement="right">
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
                {{ t('common.actions.import') }}
              </MkDropdownItem>
              <!-- 导出工具 -->
              <MkDropdownItem :disabled="!setting.tools.length" @click="handleExport">
                <template #icon><MkIcon name="icon_export_outlined" /></template>
                {{ t('common.actions.export') }}
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
        <el-option :label="t('common.options.custom')" value="customize" />
        <el-option :label="t('common.options.reference')" value="reference" />
      </el-select>
    </div>
  </div>

  <!-- 引用来源时加入节点外层表单，校验必填与引用有效性 -->
  <el-form-item v-if="setting.location === 'reference'" class="mb-0!" prop="tools.reference" :rules="referenceRules">
    <NodeCascader
      ref="referenceCascaderRef"
      :model-value="setting.reference"
      :node-model="nodeModel"
      class="w-full!"
      :placeholder="t('workflow.llm.tools.placeholder')"
      @update:model-value="updateSetting({ reference: $event })"
    />
  </el-form-item>
  <MkTable class="border" v-else-if="setting.tools.length" :data="setting.tools" size="small" row-key="function.name" :max-height="undefined">
    <el-table-column :label="t('workflow.llm.toolName.label')">
      <template #default="{ row }">
        <span class="block truncate" :title="row.function.name">{{ row.function.name }}</span>
      </template>
    </el-table-column>
    <el-table-column :label="t('workflow.llm.toolDescription.label')">
      <template #default="{ row }">
        <span class="block truncate" :title="row.function.description || '-'">{{ row.function.description || '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column :label="t('dynamicForm.fields.parameter.label')">
      <template #default="{ row }">{{ Object.keys(row.function.parameters?.properties ?? {}).length }}</template>
    </el-table-column>
    <el-table-column :label="t('common.labels.operation')" width="80">
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

  <ToolImportDialog ref="toolImportDialogRef" @submit="handleImport" />
</template>
