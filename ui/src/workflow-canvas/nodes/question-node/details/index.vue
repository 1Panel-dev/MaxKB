<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'QuestionNodeDetail' })

const { t } = useI18n({ useScope: 'global' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.systemPrompt.label') }}</h6>
      <div>{{ data.system || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.history.label') }}</h6>
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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.currentChat') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.answer') }}</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
