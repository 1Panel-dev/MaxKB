<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'LoopStartNodeDetail' })

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
      <h5 class="px-3 py-2">输入参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2"><span class="mr-1 text-N600">循环项:</span>{{ data.current_item }}</p>
        <p><span class="mr-1 text-N600">循环下标:</span>{{ data.current_index }}</p>
      </div>
    </div>
  </DetailContainer>
</template>
