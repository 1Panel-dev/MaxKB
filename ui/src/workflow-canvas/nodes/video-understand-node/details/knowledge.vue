<script setup lang="ts">
import MkVideo from '@/components/global/mk-media-preview/MkVideo.vue'
import { getFileIconUrl } from '@/utils/icon'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'VideoUnderstandKnowledgeDetails' })

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
      <h6 class="mb-2">系统提示词</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">用户提示词</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <div v-if="data.video_list?.length > 0">
          <!-- 点击卡片播放本次对话视频 -->
          <MkVideo v-for="(file, index) in data.video_list" :key="index" :src="file.url" :name="file.name || '视频'" class="w-full">
            <el-card shadow="never" class="small cursor-pointer">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(file.name || 'video.mp4')" alt="" width="24" class="shrink-0" />
                <span class="min-w-0 truncate" :title="file.name || '视频'">{{ file.name || '视频' }}</span>
              </div>
            </el-card>
          </MkVideo>
        </div>
        <div>{{ data.question || '-' }}</div>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">思考过程</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.reasoning_content" :model-value="data.reasoning_content" noImgZoomIn />
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
