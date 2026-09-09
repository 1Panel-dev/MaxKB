<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ToolCustomNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div v-if="data.index != 0" class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输入</h5>
      <div class="break-all border-t border-dashed px-3 py-2 text-N900">
        {{ data.params || '-' }}
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出</h5>
      <div class="break-all border-t border-dashed px-3 py-2 text-N900">
        {{ data.result || '-' }}
      </div>
    </div>
  </DetailContainer>
</template>
