<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ImageToVideoNodeDetail' })

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
      <h5 class="px-3 py-2">本次对话</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">负向提示词</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        {{ data.negative_prompt || '-' }}
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">首帧</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        <el-image
          v-if="typeof data.first_frame_url === 'string'"
          :src="data.first_frame_url"
          fit="cover"
          class="block h-10 w-10 rounded-md"
          :zoom-rate="1.2"
          :max-scale="7"
          :min-scale="0.2"
        />
        <div v-else-if="Array.isArray(data.first_frame_url)" class="flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.first_frame_url"
            :key="i"
            :src="f.url"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.first_frame_url.map((img: any) => img.url)"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
          />
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">末帧</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        <el-image
          v-if="typeof data.last_frame_url === 'string'"
          :src="data.last_frame_url"
          fit="cover"
          class="block h-10 w-10 rounded-md"
          :zoom-rate="1.2"
          :max-scale="7"
          :min-scale="0.2"
        />
        <div v-else-if="Array.isArray(data.last_frame_url)" class="flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.last_frame_url"
            :key="i"
            :src="f.url"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.last_frame_url.map((img: any) => img.url)"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
          />
        </div>
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
          class="image-to-video-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.image-to-video-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
