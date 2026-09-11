<script setup lang="ts">
import { computed, inject, onMounted } from 'vue'
import { cloneDeep } from 'lodash'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type { ToolFieldConfig, ToolInputField, ToolOutputField } from './types'
import InputFieldTable from './component/input/InputFieldTable.vue'
import OutputFieldTable from './component/output/OutputFieldTable.vue'

defineOptions({ name: 'WorkflowToolBaseNode' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()

// 工具参数保留 properties 顶层协议，初始化时补齐旧节点缺失的列表与标题。
if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
if (!Array.isArray(model.properties.user_output_field_list)) model.properties.user_output_field_list = []
model.properties.user_input_config = { title: '用户输入', ...(model.properties.user_input_config as ToolFieldConfig | undefined) }
model.properties.user_output_config = { title: '输出参数', ...(model.properties.user_output_config as ToolFieldConfig | undefined) }

const inputFields = computed({
  get: () => model.properties.user_input_field_list as ToolInputField[],
  set: (fields: ToolInputField[]) => {
    model.properties.user_input_field_list = cloneDeep(fields)
    refreshFields()
  },
})
const outputFields = computed({
  get: () => model.properties.user_output_field_list as ToolOutputField[],
  set: (fields: ToolOutputField[]) => {
    model.properties.user_output_field_list = cloneDeep(fields)
    refreshFields()
  },
})
const inputConfig = computed({
  get: () => model.properties.user_input_config as ToolFieldConfig,
  set: (config: ToolFieldConfig) => {
    model.properties.user_input_config = cloneDeep(config)
  },
})
const outputConfig = computed({
  get: () => model.properties.user_output_config as ToolFieldConfig,
  set: (config: ToolFieldConfig) => {
    model.properties.user_output_config = cloneDeep(config)
  },
})

// 增删、编辑和排序后先刷新全局变量，再失效下游字段缓存。
function refreshFields() {
  model.graphModel.eventCenter.emit('refreshFieldList', undefined)
  const startNode = model.graphModel.getNodeModelById(WorkflowNodeType.ToolStartNode) as WorkflowNodeModel | undefined
  startNode?.clearNextNodeField(true)
}

onMounted(refreshFields)
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card space-y-4">
      <!-- 用户输入 -->
      <InputFieldTable v-model="inputFields" v-model:config="inputConfig" />
      <!-- 输出参数 -->
      <OutputFieldTable v-model="outputFields" v-model:config="outputConfig" />
    </div>
  </NodeContainer>
</template>
