<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'DocumentExtractNodeDetail' })

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
      <h6 class="flex items-center gap-1 mb-2">
        <span>输出参数</span>
        <MkTooltip content="多个文件的内容会按文件顺序拼接输出" placement="right">
          <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
        </MkTooltip>
      </h6>

      <el-scrollbar max-height="200">
        <div class="space-y-2">
          <template v-for="(file_content, index) in data.content" :key="index">
            <el-card shadow="never">
              <h4 class="mb-1">{{ file_content.name }}</h4>
              <MdPreview v-if="file_content.content" :model-value="file_content.content" no-img-zoom-in />
              <template v-else>-</template>
            </el-card>
          </template>
        </div>
      </el-scrollbar>
    </div>
  </DetailContainer>
</template>
