<script setup lang="ts">
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import { getFileIconUrl } from '@/utils/icon'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'AiChatKnowledgeDetails' })

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
      <h6 class="mb-2">系统提示词</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <!-- 用户提示词 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">用户提示词</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <template v-if="Array.isArray(data.question)">
          <div v-for="(item, qIndex) in data.question" :key="qIndex">
            <!-- 查看本次对话图片 -->
            <ImageUploadCard
              v-if="item.type === 'image_url'"
              :file="{ name: '图片', status: 'success' }"
              :src="item.image_url?.url || item.image_url"
              :size="32"
              :show-remove="false"
              :preview-src-list="[item.image_url?.url || item.image_url]"
            />
            <!-- 点击卡片播放本次对话视频 -->
            <MkVideo v-else-if="item.type === 'video_url'" :src="item.video_url?.url || item.video_url" name="视频" class="w-full">
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl('video.mp4')" alt="" width="24" class="shrink-0" />
                  <span class="min-w-0 truncate">视频</span>
                </div>
              </el-card>
            </MkVideo>
            <div v-else-if="item.type === 'text'">{{ item.text }}</div>
            <div v-else>{{ item }}</div>
          </div>
        </template>
        <template v-else>
          {{ data.question || '-' }}
        </template>
      </div>
    </div>

    <!-- 思考过程 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">思考过程</h6>
      <div class="whitespace-pre-wrap">
        {{ data.reasoning_content || '-' }}
      </div>
    </div>

    <!-- AI 回答 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">AI 回答</h6>
      <div>
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
