<template>
  <NodeContainer :node-model="model">
    <div class="text-sm text-N600">终止当前循环，跳出循环体</div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { inject, onMounted } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'

defineOptions({ name: 'WorkflowLoopBreakNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

onMounted(() => {
  if (!model.properties.node_data) {
    set(model.properties, 'node_data', { condition: 'and', condition_list: [] })
  }
})
</script>
