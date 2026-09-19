<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'McpNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">工具</h6>
      <div>
        {{ data.mcp_tool || '-' }}
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">工具参数</h6>
      <div class="space-y-2">
        <p v-for="(value, name) in data.tool_params" :key="name">
          <span class="text-N600">{{ name }}：</span>{{ value }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输出参数</h6>
      <div class="break-all space-y-2">
        <p v-for="(f, i) in data.result" :key="i"><span class="text-N600">result：</span>{{ f }}</p>
      </div>
    </div>
  </DetailContainer>
</template>
