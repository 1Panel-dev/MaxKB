<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'TextToSpeechNodeDetail' })

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
        <p class="mb-2 text-N600">文本内容:</p>
        <MdPreview
          v-if="data.content"
          editor-id="preview-only"
          :model-value="data.content"
          class="text-to-speech-content"
          noImgZoomIn
        />
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2 text-N600">音频文件:</p>
        <div v-if="data.answer" v-html="data.answer" />
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.text-to-speech-content.md-editor) {
  background: transparent;
  height: auto;
}
</style>
