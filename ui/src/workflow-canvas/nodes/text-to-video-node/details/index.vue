<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'TextToVideoNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" show-tokens />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">负向提示词</h6>
      <div class="whitespace-pre-wrap">
        {{ data.negative_prompt || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">AI 回答</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
