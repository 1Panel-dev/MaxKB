<script setup lang="ts">
import { Warning } from '@element-plus/icons-vue'
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'DocumentExtractNodeDetail' })

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
      <h5 class="flex items-center gap-1 px-3 py-2">
        <span>输出参数</span>
        <el-tooltip effect="dark" content="多个文件的内容会按文件顺序拼接输出" placement="right">
          <el-icon class="text-N600"><Warning /></el-icon>
        </el-tooltip>
      </h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <el-scrollbar height="200">
          <div
            v-for="(file_content, index) in data.content"
            :key="index"
            class="mb-2 overflow-hidden rounded-md bg-N100"
          >
            <MdPreview
              v-if="file_content"
              editor-id="preview-only"
              :model-value="file_content"
              class="document-extract-content"
              noImgZoomIn
            />
            <template v-else>-</template>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.document-extract-content.md-editor) {
  background: transparent;
  height: auto;
}
</style>
