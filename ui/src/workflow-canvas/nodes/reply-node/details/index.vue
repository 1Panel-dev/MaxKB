<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ReplyNodeDetail' })

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
      <h5 class="px-3 py-2">回复内容</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <el-scrollbar height="150">
          <MdPreview
            v-if="data.answer"
            editor-id="preview-only"
            :model-value="data.answer"
            class="reply-answer"
            noImgZoomIn
          />
          <template v-else>-</template>
        </el-scrollbar>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.reply-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
