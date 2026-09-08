<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'AiChatApplicationDetails' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" show-tokens />
    </template>

    <!-- 系统提示词 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">系统提示词</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">{{ data.system || '-' }}</div>
    </div>

    <!-- 历史记录 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">历史记录</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex" class="my-1">
            <span class="mr-1 text-N600">{{ history.role }}:</span>
            <span>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <!-- 本次对话 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">本次对话</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        <template v-if="Array.isArray(data.question)">
          <div v-for="(item, qIndex) in data.question" :key="qIndex" class="mb-2">
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
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">思考过程</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        {{ data.reasoning_content || '-' }}
      </div>
    </div>

    <!-- AI 回答 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">AI 回答</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <MdPreview
          v-if="data.answer"
          editor-id="preview-only"
          :model-value="data.answer"
          class="ai-chat-answer"
          noImgZoomIn
        />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
/* 只读回答需要自适应高度并融入区块灰底，覆盖全局 Markdown 编辑器的固定高度与背景。 */
:deep(.ai-chat-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
