<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'VideoUnderstandApplicationDetails' })

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
      <h5 class="px-3 py-2">历史记录</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex" class="my-1">
            <span class="mr-1 text-N600">{{ history.role }}:</span>
            <template v-if="Array.isArray(history.content)">
              <span v-for="(h, i) in history.content" :key="i">
                <video
                  v-if="h.type === 'video_url'"
                  :src="h.video_url.url"
                  class="mr-2 inline-block rounded-md"
                  style="width: 40px; height: 40px"
                />
                <span v-else>{{ h.text }}<br /></span>
              </span>
            </template>
            <span v-else>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">本次对话</h5>
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
