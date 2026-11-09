<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'LlmNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2)
}
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
    <!-- 系统提示词 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">用户提示词</h6>
      <div>{{ data.prompt || '-' }}</div>
    </div>

    <!-- 消息列表 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">上下文</h6>
      <div class="space-y-2">
        <template v-if="data.message_list?.length > 0">
          <p v-for="(message, messageIndex) in data.message_list" :key="messageIndex" class="whitespace-pre-wrap">
            <span class="text-N600">{{ message.role }}：</span>
            <span>{{ message.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>
    <!-- 结束原因 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">结束原因</h6>
      <div>{{ data.finish_reason || '-' }}</div>
    </div>
    <!-- 回答内容 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">回答内容</h6>
      <div>
        <MdPreview v-if="data.content" :model-value="data.content" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>

    <!-- 拒答内容 -->
    <div v-if="data.is_refusal" class="mk-gray-card-sm">
      <h6 class="mb-2">拒答内容</h6>
      <div class="whitespace-pre-wrap">{{ data.refusal || '-' }}</div>
    </div>

    <!-- 工具调用 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">工具调用</h6>
      <div class="whitespace-pre-wrap break-all">
        {{ data.tool_calls?.length > 0 ? formatJson(data.tool_calls) : '-' }}
      </div>
    </div>


  </DetailContainer>
</template>
