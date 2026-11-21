<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'VideoUnderstandKnowledgeDetails' })

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
      <h6 class="mb-2">{{ t('workflow.systemPrompt.label') }}</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.userPrompt.label') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <div v-if="data.video_list?.length > 0">
          <!-- 点击卡片播放本次对话视频 -->
          <MkVideo v-for="(file, index) in data.video_list" :key="index" :src="file.url" :name="file.name || t('upload.types.video')" class="w-full">
            <el-card shadow="never" class="small cursor-pointer">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(file.name || 'video.mp4')" alt="" width="24" class="shrink-0" />
                <span class="min-w-0 truncate" :title="file.name || t('upload.types.video')">{{ file.name || t('upload.types.video') }}</span>
              </div>
            </el-card>
          </MkVideo>
        </div>
        <div>{{ data.question || '-' }}</div>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.thinking.process') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.reasoning_content" :model-value="data.reasoning_content" noImgZoomIn />
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
