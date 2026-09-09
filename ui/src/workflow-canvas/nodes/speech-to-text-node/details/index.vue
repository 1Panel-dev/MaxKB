<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'SpeechToTextNodeDetail' })

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
        <div v-if="data.audio_list?.length > 0">
          <p class="mb-2 text-N600">音频文件:</p>
          <div class="flex flex-wrap gap-2">
            <audio
              v-for="(f, i) in data.audio_list"
              :key="i"
              :src="f.url"
              controls
              class="rounded-md"
              style="width: 300px; height: 43px"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <div
          v-for="(file_content, index) in data.content"
          :key="index"
          class="mb-2 overflow-hidden rounded-md bg-N100"
        >
          <MdPreview
            v-if="file_content"
            editor-id="preview-only"
            :model-value="file_content"
            class="speech-to-text-content"
            noImgZoomIn
          />
          <template v-else>-</template>
        </div>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.speech-to-text-content.md-editor) {
  background: transparent;
  height: auto;
}
</style>
