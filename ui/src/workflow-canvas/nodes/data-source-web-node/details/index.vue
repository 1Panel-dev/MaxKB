<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'DataSourceWebNodeDetail' })

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
      <h5 class="px-3 py-2">输入参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2">
          <span class="mr-1 text-N600">选择器:</span>{{ data.selector }}
        </p>
        <p>
          <span class="mr-1 text-N600">文档地址:</span>{{ data.source_url }}
        </p>
      </div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <el-scrollbar height="200">
          <div
            v-for="(file_content, index) in data.document_list"
            :key="index"
            class="mb-2 overflow-hidden rounded-md bg-N100"
          >
            <h4 class="mb-1">{{ file_content.name }}</h4>
            <MdPreview
              v-if="file_content.content"
              :model-value="file_content.content"
              class="data-source-web-content"
              no-img-zoom-in
            />
            <template v-else>-</template>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.data-source-web-content.md-editor) {
  background: transparent;
  height: auto;
}
</style>
