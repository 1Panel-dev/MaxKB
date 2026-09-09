<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ApplicationNodeDetail' })

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
        <p class="mb-2"><span class="mr-1 text-N600">问题:</span>{{ data.question || '-' }}</p>

        <p v-for="(f, i) in data.global_fields" :key="i" class="mb-2">
          <span class="mr-1 text-N600">{{ f.label }}:</span>{{ f.value }}
        </p>

        <div v-if="data.document_list?.length > 0" class="mb-2">
          <p class="mb-1 text-N600">文档:</p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(f, i) in data.document_list"
              :key="i"
              class="flex items-center rounded-md bg-white px-2 py-1"
            >
              <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
              <span class="ml-1 max-w-[200px] truncate" :title="f?.name">{{ f?.name }}</span>
            </div>
          </div>
        </div>

        <div v-if="data.image_list?.length > 0" class="mb-2">
          <p class="mb-1 text-N600">图片:</p>
          <div class="flex flex-wrap gap-2">
            <el-image
              v-for="(f, i) in data.image_list"
              :key="i"
              :src="f.url"
              fit="cover"
              class="block h-10 w-10 rounded-md"
              :preview-src-list="data.image_list.map((img: any) => img.url)"
              :initial-index="i"
              :zoom-rate="1.2"
              :max-scale="7"
              :min-scale="0.2"
            />
          </div>
        </div>

        <div v-if="data.audio_list?.length > 0" class="mb-2">
          <p class="mb-1 text-N600">音频文件:</p>
          <audio
            v-for="(f, i) in data.audio_list"
            :key="i"
            :src="f.url"
            controls
            class="rounded-md"
            style="width: 300px; height: 43px"
          />
        </div>

        <div v-if="data.video_list?.length > 0" class="mb-2">
          <p class="mb-1 text-N600">视频:</p>
          <video
            v-for="(f, i) in data.video_list"
            :key="i"
            :src="f.url"
            controls
            autoplay
            class="block rounded-md"
            style="width: 170px"
          />
        </div>

        <div v-if="data.other_list?.length > 0" class="mb-2">
          <p class="mb-1 text-N600">其他:</p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(f, i) in data.other_list"
              :key="i"
              class="flex items-center rounded-md bg-white px-2 py-1"
            >
              <img :src="getFileIconUrl(f?.name)" alt="" width="24" />
              <span class="ml-1 max-w-[200px] truncate" :title="f?.name">{{ f?.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MdPreview
          v-if="data.answer"
          editor-id="preview-only"
          :model-value="data.answer"
          class="application-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.application-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
