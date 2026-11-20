<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'McpNodeDetail' })
const { t } = useI18n({ useScope: 'global' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('tool.title') }}</h6>
      <div>
        {{ data.mcp_tool || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.mcp.parameters.label') }}</h6>
      <div class="space-y-2">
        <p v-for="(value, name) in data.tool_params" :key="name">
          <span class="text-N600">{{ name }}：</span>
          {{ value }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('execution.details.outputParams') }}</h6>
      <div class="break-all space-y-2">
        <p v-for="(f, i) in data.result" :key="i">
          <span class="text-N600">result：</span>
          {{ f }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
