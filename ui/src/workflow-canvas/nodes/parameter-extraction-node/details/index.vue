<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/Execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/Execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/Execution-details/types'

defineOptions({ name: 'ParameterExtractionNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输入参数</h6>
      <div class="whitespace-pre-wrap">
        {{ data.request || '-' }}
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.result" :key="i">
          <span class="text-N600">{{ i }}：</span>{{ f }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
