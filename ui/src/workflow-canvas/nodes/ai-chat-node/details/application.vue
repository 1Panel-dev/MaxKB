<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'AiChatApplicationDetails' })
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

    <!-- 系统提示词 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.systemPrompt.label') }}</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <!-- 历史记录 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.history.label') }}</h6>
      <div class="space-y-2">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex">
            <span class="text-N600">{{ history.role }}：</span>
            <span>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <!-- 本次对话 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.currentChat') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <p class="mb-1 text-N600" v-if="data?.image_list?.length > 0">{{ t('upload.types.image') }}：</p>
        <!-- 查看本次对话图片 -->
        <div v-if="data?.image_list?.length > 0" class="flex flex-wrap gap-2">
          <template v-for="(imageItem, qIndex) in data?.image_list" :key="qIndex">
            <ImageUploadCard
              :file="{ name: t('upload.types.image'), status: 'success' }"
              :src="imageItem.url || imageItem"
              :size="58"
              :show-remove="false"
              :preview-src-list="[imageItem.url || imageItem]"
            />
          </template>
        </div>
        <p class="mb-1 text-N600" v-if="data?.video_list?.length > 0">{{ t('upload.types.video') }}：</p>
        <!-- 查看本次对话视频 -->
        <div v-if="data?.video_list?.length > 0" class="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <template v-for="(videoItem, qIndex) in data?.video_list" :key="qIndex">
            <MkVideo :src="videoItem.url || videoItem" :name="videoItem.url" class="w-60 max-w-full">
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl('video.mp4')" alt="" width="24" class="shrink-0" />
                  <span class="min-w-0 truncate">{{ videoItem.url || videoItem }}</span>
                </div>
              </el-card>
            </MkVideo>
          </template>
        </div>

        <MdPreview v-if="data.question?.content" :model-value="data.question?.content" noImgZoomIn />
      </div>
    </div>

    <!-- 思考过程 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.thinking.process') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ data.reasoning_content || '-' }}
      </div>
    </div>

    <!-- AI 回答 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">AI {{ t('workflow.answer.label') }}</h6>
      <div>
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
