<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'VideoUnderstandApplicationDetails' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" show-tokens />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">系统提示词</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">历史记录</h6>
      <div class="space-y-2">
        <template v-if="data.history_message?.length > 0">
          <p v-for="(history, historyIndex) in data.history_message" :key="historyIndex" class="mb-2 last:mb-0">
            <span class="text-N600">{{ history.role }}：</span>
            <template v-if="Array.isArray(history.content)">
              <span v-for="(h, i) in history.content" :key="i">
                <video v-if="h.type === 'video_url'" :src="h.video_url.url" class="mr-2 inline-block rounded-md" style="width: 40px; height: 40px" />
                <span v-else>{{ h.text }}<br /></span>
              </span>
            </template>
            <span v-else>{{ history.content }}</span>
          </p>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <div v-if="data.video_list?.length > 0" class="flex flex-wrap gap-2">
          <video v-for="(f, i) in data.video_list" :key="i" :src="f.url" controls autoplay class="block rounded-md" style="width: 100px" />
        </div>
        <div>{{ data.question || '-' }}</div>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">思考过程</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.reasoning_content" :model-value="data.reasoning_content" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">AI 回答</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
