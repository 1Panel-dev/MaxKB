<script setup lang="ts">
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ImageToVideoNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" show-tokens />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">负向提示词</h6>
      <div class="whitespace-pre-wrap">
        {{ data.negative_prompt || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">首帧</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <!-- 查看首帧图片 -->
        <ImageUploadCard
          v-if="typeof data.first_frame_url === 'string'"
          :file="{ name: '首帧', status: 'success' }"
          :src="data.first_frame_url"
          :size="32"
          :show-remove="false"
          :preview-src-list="[data.first_frame_url]"
        />
        <div v-else-if="Array.isArray(data.first_frame_url)" class="flex flex-wrap gap-2">
          <!-- 查看首帧图片列表 -->
          <ImageUploadCard
            v-for="(file, index) in data.first_frame_url"
            :key="index"
            :file="{ ...file, name: file.name || '首帧', status: 'success' }"
            :src="file.url"
            :size="32"
            :show-remove="false"
            :preview-src-list="data.first_frame_url.map((image: { url: string }) => image.url)"
            :initial-index="index"
          />
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">末帧</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <!-- 查看末帧图片 -->
        <ImageUploadCard
          v-if="typeof data.last_frame_url === 'string'"
          :file="{ name: '末帧', status: 'success' }"
          :src="data.last_frame_url"
          :size="32"
          :show-remove="false"
          :preview-src-list="[data.last_frame_url]"
        />
        <div v-else-if="Array.isArray(data.last_frame_url)" class="flex flex-wrap gap-2">
          <!-- 查看末帧图片列表 -->
          <ImageUploadCard
            v-for="(file, index) in data.last_frame_url"
            :key="index"
            :file="{ ...file, name: file.name || '末帧', status: 'success' }"
            :src="file.url"
            :size="32"
            :show-remove="false"
            :preview-src-list="data.last_frame_url.map((image: { url: string }) => image.url)"
            :initial-index="index"
          />
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">AI 回答</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
