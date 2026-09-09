<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'VideoUnderstandKnowledgeDetails' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" show-tokens />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">系统提示词</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">{{ data.system || '-' }}</div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">用户提示词</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        <div v-if="data.video_list?.length > 0" class="mb-2 flex flex-wrap gap-2">
          <video
            v-for="(f, i) in data.video_list"
            :key="i"
            :src="f.url"
            controls
            autoplay
            class="block rounded-md"
            style="width: 100px"
          />
        </div>
        <div>{{ data.question || '-' }}</div>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">思考过程</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MdPreview
          v-if="data.reasoning_content"
          editor-id="preview-only"
          :model-value="data.reasoning_content"
          class="video-understand-reasoning"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">AI 回答</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MdPreview
          v-if="data.answer"
          editor-id="preview-only"
          :model-value="data.answer"
          class="video-understand-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.video-understand-reasoning.md-editor),
:deep(.video-understand-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
