<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'AiChatApplicationDetails' })

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
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">系统提示词</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <!-- 历史记录 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">历史记录</h6>
      <div class="space-y-2">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex">
            <span class="text-N600">{{ history.role }}1111：</span>
            <span>{{ history.content }}11</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <!-- 本次对话 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <template v-if="Array.isArray(data.question)">
          <div v-for="(item, qIndex) in data.question" :key="qIndex">
            <el-image
              v-if="item.type === 'image_url'"
              :src="item.image_url?.url || item.image_url"
              fit="cover"
              class="block h-10 w-10 rounded-md"
              :zoom-rate="1.2"
              :max-scale="7"
              :min-scale="0.2"
            />
            <video
              v-else-if="item.type === 'video_url'"
              :src="item.video_url?.url || item.video_url"
              class="block w-[170px] rounded-md"
              autoplay
              controls
            />
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
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">思考过程</h6>
      <div class="whitespace-pre-wrap">
        {{ data.reasoning_content || '-' }}
      </div>
    </div>

    <!-- AI 回答 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">AI 回答</h6>
      <div>
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
