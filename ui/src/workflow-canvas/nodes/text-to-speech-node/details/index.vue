<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'TextToSpeechNodeDetail' })

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
      <h6 class="mb-2">{{ t('workflow.executionResult.inputParams') }}</h6>
      <div class="space-y-2">
        <p class="text-N600">{{ t('workflow.textToSpeech.content.label') }}：</p>
        <MdPreview v-if="data.content" :model-value="data.content" noImgZoomIn />
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.outputParams') }}</h6>
      <div class="space-y-2">
        <p class="text-N600">{{ t('workflow.audioFile.label') }}：</p>
        <div v-if="data.answer" v-html="data.answer" />
      </div>
    </div>
  </DetailContainer>
</template>
