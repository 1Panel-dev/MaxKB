<script setup lang="ts">
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">系统提示词</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">历史记录</h6>
      <div class="space-y-2">
        <template v-if="data.history_message?.length > 0">
          <div v-for="(history, historyIndex) in data.history_message" :key="historyIndex" class="mb-2 last:mb-0">
            <span class="mr-1 text-N600">{{ history.role }}：</span>
            <template v-if="Array.isArray(history.content)">
              <div v-for="(h, i) in history.content" :key="i">
                <!-- 查看历史对话图片 -->
                <ImageUploadCard
                  v-if="h.type === 'image_url'"
                  :file="{ name: '图片', status: 'success' }"
                  :src="h.image_url.url"
                  :size="104"
                  :show-remove="false"
                  :preview-src-list="[h.image_url.url]"
                />
                <span v-else>
                  {{ h.text }}
                  <br />
                </span>
              </div>
            </template>
            <span v-else>{{ history.content }}</span>
          </div>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <div v-if="data.image_list?.length > 0" class="flex flex-wrap gap-2">
          <!-- 查看本次对话图片 -->
          <ImageUploadCard
            v-for="(f, i) in data.image_list"
            :key="i"
            :file="{ ...f, name: f.name || '图片', status: 'success' }"
            :src="f.url || (f.file_id ? `./oss/file/${f.file_id}` : '')"
            :size="104"
            :show-remove="false"
            :preview-src-list="data.image_list.map((img: any) => img.url || (img.file_id ? `./oss/file/${img.file_id}` : ''))"
            :initial-index="Number(i)"
          />
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
