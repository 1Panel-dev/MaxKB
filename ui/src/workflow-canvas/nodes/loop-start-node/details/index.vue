<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/Execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/Execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/Execution-details/types'

defineOptions({ name: 'LoopStartNodeDetail' })

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
      <h6 class="mb-2">输入参数</h6>
      <div class="space-y-2">
        <p><span class="text-N600">循环项：</span>{{ data.current_item }}</p>
        <p><span class="text-N600">循环下标：</span>{{ data.current_index }}</p>
      </div>
    </div>
  </DetailContainer>
</template>
