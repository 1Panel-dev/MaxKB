<script setup lang="ts">
import { inject } from 'vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'

defineOptions({ name: 'WorkflowDataSourceWebNode' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card text-N600">暂无配置项</div>
  </NodeContainer>
</template>
