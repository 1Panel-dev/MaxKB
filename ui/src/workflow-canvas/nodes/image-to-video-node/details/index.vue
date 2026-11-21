<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'ImageToVideoNodeDetail' })

const { t } = useI18n({ useScope: 'global' })

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
      <h6 class="mb-2">{{ t('execution.details.currentChat') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.negativePrompt.detailLabel') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ data.negative_prompt || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.imageToVideo.firstFrame.shortLabel') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <!-- 查看首帧图片 -->
        <ImageUploadCard
          v-if="typeof data.first_frame_url === 'string'"
          :file="{ name: t('workflow.imageToVideo.firstFrame.shortLabel'), status: 'success' }"
          :src="data.first_frame_url"
          :size="58"
          :show-remove="false"
          :preview-src-list="[data.first_frame_url]"
        />
        <div v-else-if="Array.isArray(data.first_frame_url)" class="flex flex-wrap gap-2">
          <!-- 查看首帧图片列表 -->
          <template v-for="(file, index) in data.first_frame_url" :key="index">
            <ImageUploadCard
              :file="{ ...file, name: file.name || t('workflow.imageToVideo.firstFrame.shortLabel'), status: 'success' }"
              :src="file.url"
              :size="58"
              :show-remove="false"
              :preview-src-list="data.first_frame_url.map((image: { url: string }) => image.url)"
            />
          </template>
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.imageToVideo.lastFrame.shortLabel') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <!-- 查看末帧图片 -->
        <ImageUploadCard
          v-if="typeof data.last_frame_url === 'string'"
          :file="{ name: t('workflow.imageToVideo.lastFrame.shortLabel'), status: 'success' }"
          :src="data.last_frame_url"
          :size="58"
          :show-remove="false"
          :preview-src-list="[data.last_frame_url]"
        />
        <div v-else-if="Array.isArray(data.last_frame_url)" class="flex flex-wrap gap-2">
          <!-- 查看末帧图片列表 -->
          <template v-for="(file, index) in data.last_frame_url" :key="index">
            <ImageUploadCard
              :file="{ ...file, name: file.name || t('workflow.imageToVideo.lastFrame.shortLabel'), status: 'success' }"
              :src="file.url"
              :size="58"
              :show-remove="false"
              :preview-src-list="data.last_frame_url.map((image: { url: string }) => image.url)"
            />
          </template>
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.answer.aiLabel') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
