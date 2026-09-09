<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'McpNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">工具</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2"><span class="mr-1 text-N600">工具:</span>{{ data.mcp_tool }}</p>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">工具参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p v-for="(value, name) in data.tool_params" :key="name" class="mb-2">
          <span class="mr-1 text-N600">{{ name }}:</span>{{ value }}
        </p>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="break-all border-t border-dashed px-3 py-2 text-N900">
        <p v-for="(f, i) in data.result" :key="i" class="mb-2">
          <span class="mr-1 text-N600">result:</span>{{ f }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
