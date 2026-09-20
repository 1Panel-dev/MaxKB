<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ToolCustomNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 输入 -->
    <div v-if="data.index != 0" class="mk-gray-card-sm">
      <h6 class="mb-2">输入</h6>
      <div class="break-all">
        {{ data.params || '-' }}
      </div>
    </div>

    <!-- 输出 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出</h6>
      <div class="break-all">
        {{ data.result || '-' }}
      </div>
    </div>
  </DetailContainer>
</template>
