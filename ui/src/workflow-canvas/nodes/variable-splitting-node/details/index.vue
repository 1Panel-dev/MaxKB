<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'VariableSplittingNodeDetail' })
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
      <h6 class="mb-2">{{ t('execution.details.inputParams') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ data.request || '-' }}
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('execution.details.outputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.result" :key="i">
          <span class="text-N600">{{ i }}：</span>
          {{ f }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
