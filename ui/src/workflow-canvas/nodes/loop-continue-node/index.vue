<template>
  <NodeContainer :node-model="model">
    <div class="text-sm text-N600">结束当前迭代，进入下一次循环</div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { inject, onMounted } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'

defineOptions({ name: 'WorkflowLoopContinueNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

onMounted(() => {
  if (!model.properties.node_data) {
    set(model.properties, 'node_data', { condition: 'and', condition_list: [] })
  }
})
</script>
