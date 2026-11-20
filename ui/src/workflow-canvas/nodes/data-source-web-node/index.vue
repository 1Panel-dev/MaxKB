<script setup lang="ts">
import { inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'

defineOptions({ name: 'WorkflowDataSourceWebNode' })
const { t } = useI18n({ useScope: 'global' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>
    <div class="mk-gray-card text-N600">{{ t('workflow.webSource.noConfiguration') }}</div>
  </NodeContainer>
</template>
