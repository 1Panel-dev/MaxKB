<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/Execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/Execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/Execution-details/types'

defineOptions({ name: 'IntentNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
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
            <span class="text-N600">{{ history.role }}：</span>
            <span>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <!-- 本次对话 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <!-- 回答 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">回答</h6>
      <div>
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
