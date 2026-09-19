<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ImageUnderstandApplicationDetails' })

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
            <span class="mr-1 text-N600">{{ history.role }}：</span>
            <template v-if="Array.isArray(history.content)">
              <span v-for="(h, i) in history.content" :key="i">
                <el-image
                  v-if="h.type === 'image_url'"
                  :src="h.image_url.url"
                  fit="cover"
                  class="mr-2 inline-block h-10 w-10 rounded-md"
                  :zoom-rate="1.2"
                  :max-scale="7"
                  :min-scale="0.2"
                />
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
        <div v-if="data.image_list?.length > 0" class="flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.image_list"
            :key="i"
            :src="f.url || (f.file_id ? `./oss/file/${f.file_id}` : '')"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.image_list.map((img: any) => img.url || (img.file_id ? `./oss/file/${img.file_id}` : ''))"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
          />
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
