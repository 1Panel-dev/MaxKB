<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'ToolLibNodeDetail' })

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

    <div v-if="data.index != 0" class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.input') }}</h6>
      <div class="break-all">
        {{ data.params || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.output') }}</h6>
      <div class="break-all">
        {{ data.result || '-' }}
      </div>
    </div>
  </DetailContainer>
</template>
