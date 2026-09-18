<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/Execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/Execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/Execution-details/types'

defineOptions({ name: 'ReplyNodeDetail' })

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
      <h6 class="mb-2">回复内容</h6>
      <div>
        <el-scrollbar max-height="150">
          <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
          <template v-else>-</template>
        </el-scrollbar>
      </div>
    </div>
  </DetailContainer>
</template>
