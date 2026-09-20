<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'TextToSpeechNodeDetail' })

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
        <p class="text-N600">文本内容：</p>
        <MdPreview v-if="data.content" :model-value="data.content" noImgZoomIn />
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <p class="text-N600">音频文件：</p>
        <div v-if="data.answer" v-html="data.answer" />
      </div>
    </div>
  </DetailContainer>
</template>
