<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ImageUnderstandApplicationDetails' })

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
                <el-image
                  v-if="h.type === 'image_url'"
                  :src="h.image_url.url"
                  fit="cover"
                  class="mr-2 inline-block h-10 w-10 rounded-md"
                  :zoom-rate="1.2"
                  :max-scale="7"
                  :min-scale="0.2"
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
        <div v-if="data.image_list?.length > 0" class="mb-2 flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.image_list"
            :key="i"
            :src="f.url || (f.file_id ? `./oss/file/${f.file_id}` : '')"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.image_list.map((img: any) => img.url || (img.file_id ? `./oss/file/${img.file_id}` : ''))"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
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
          class="image-understand-reasoning"
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
          class="image-understand-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.image-understand-reasoning.md-editor),
:deep(.image-understand-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
