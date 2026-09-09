<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'QuestionNodeDetail' })

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
      <h5 class="px-3 py-2">系统提示词</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">{{ data.system || '-' }}</div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">历史记录</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex" class="my-1">
            <span class="mr-1 text-N600">{{ history.role }}:</span>
            <span>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">本次对话</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">回答</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MdPreview
          v-if="data.answer"
          editor-id="preview-only"
          :model-value="data.answer"
          class="question-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.question-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
