<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import ImageUploadCard from '@/components/mk-drag-upload/ImageUploadCard.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'ImageUnderstandKnowledgeDetails' })

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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.systemPrompt.label') }}</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.currentChat') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <div v-if="data.image_list?.length > 0" class="flex flex-wrap gap-2">
          <!-- 查看本次对话图片 -->
          <ImageUploadCard
            v-for="(f, i) in data.image_list"
            :key="i"
            :file="{ ...f, name: f.name || t('upload.types.image'), status: 'success' }"
            :src="f.url || (f.file_id ? `./oss/file/${f.file_id}` : '')"
            :size="58"
            :show-remove="false"
            :preview-src-list="data.image_list.map((img: any) => img.url || (img.file_id ? `./oss/file/${img.file_id}` : ''))"
          />
        </div>
        <div>{{ data.question || '-' }}</div>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.thinking.process') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.reasoning_content" :model-value="data.reasoning_content" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">AI {{ t('workflow.answer.label') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
