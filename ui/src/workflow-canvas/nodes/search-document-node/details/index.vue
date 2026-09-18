<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/Execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/Execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/Execution-details/types'

defineOptions({ name: 'SearchDocumentNodeDetail' })

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
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <p>
          <span class="text-N600">knowledge_list：</span>
          {{ data.knowledge_items?.map((v: any) => v.name).join(',') }}
        </p>
        <p>
          <span class="text-N600">document_list：</span>
          {{ data.document_items?.map((v: any) => v.name).join(',') }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
