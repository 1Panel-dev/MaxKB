<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'DataSourceWebNodeDetail' })

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
      <div class="space-y-2">
        <p><span class="mr-1 text-N600">选择器：</span>{{ data.selector }}</p>
        <p><span class="mr-1 text-N600">文档地址：</span>{{ data.source_url }}</p>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输出参数</h6>

      <el-scrollbar max-height="200">
        <div class="space-y-2">
          <template v-for="(file_content, index) in data.document_list" :key="index">
            <el-card shadow="never">
              <h6 class="mb-1">{{ file_content.name }}</h6>
              <MdPreview v-if="file_content.content" :model-value="file_content.content" no-img-zoom-in />
              <template v-else>-</template>
            </el-card>
          </template>
        </div>
      </el-scrollbar>
    </div>
  </DetailContainer>
</template>
