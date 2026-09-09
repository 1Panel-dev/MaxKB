<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'SearchDocumentNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2">
          <span class="mr-1 text-N600">knowledge_list:</span>
          {{ data.knowledge_items?.map((v: any) => v.name).join(',') }}
        </p>
        <p>
          <span class="mr-1 text-N600">document_list:</span>
          {{ data.document_items?.map((v: any) => v.name).join(',') }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
