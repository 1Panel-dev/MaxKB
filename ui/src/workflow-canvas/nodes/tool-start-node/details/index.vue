<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ToolStartNodeDetail' })

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
      <h6 class="mb-2">输入参数</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.global_fields" :key="i">
          <span class="text-N600">{{ f.label }}：</span>{{ f.value }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
