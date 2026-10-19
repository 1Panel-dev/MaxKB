<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ReplyNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

const contentType = computed(() => props.data.content_type || 'TEXT')
const sanitizedHtml = computed(() => (contentType.value === 'HTML' ? DOMPurify.sanitize(String(props.data.answer ?? '')) : ''))
const toolAnswer = computed(() => (contentType.value === 'TOOL' ? JSON.stringify(props.data.answer ?? [], null, 2) : ''))
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">回复内容</h6>
      <div>
        <el-scrollbar max-height="150">
          <template v-if="!data.answer || (contentType === 'TOOL' && !data.answer.length)">-</template>
          <!-- eslint-disable-next-line vue/no-v-html -- 内容已经 DOMPurify 净化 -->
          <div v-else-if="contentType === 'HTML'" v-html="sanitizedHtml" />
          <pre v-else-if="contentType === 'TOOL'" class="whitespace-pre-wrap break-all">{{ toolAnswer }}</pre>
          <MdPreview v-else :model-value="data.answer" noImgZoomIn />
        </el-scrollbar>
      </div>
    </div>
  </DetailContainer>
</template>
