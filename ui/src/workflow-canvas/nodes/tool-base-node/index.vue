<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import InputFieldTable from './component/input/InputFieldTable.vue'
import OutputFieldTable from './component/output/OutputFieldTable.vue'

defineOptions({ name: 'WorkflowToolBaseNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const model = getModel()

const formData = computed({
  get: () => model.properties,
  set: (value) => set(model.properties, 'node_data', value),
})

onMounted(() => {
  if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
  if (!Array.isArray(model.properties.user_output_field_list)) model.properties.user_output_field_list = []
  if (!model.properties.user_input_config) model.properties.user_input_config = { title: '用户输入' }
  if (!model.properties.user_output_config) model.properties.user_output_config = { title: '输出参数' }
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <InputFieldTable :node-model="model" />
    <OutputFieldTable :node-model="model" />
  </NodeContainer>
</template>