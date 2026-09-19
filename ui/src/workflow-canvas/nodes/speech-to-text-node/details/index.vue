<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'SpeechToTextNodeDetail' })

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
      <div>
        <div v-if="data.audio_list?.length > 0">
          <p class="mb-2 text-N600">音频文件：</p>
          <div class="flex flex-wrap gap-2">
            <audio v-for="(f, i) in data.audio_list" :key="i" :src="f.url" controls class="rounded-md" style="width: 300px; height: 43px" />
          </div>
        </div>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <template v-for="(file_content, index) in data.content" :key="index">
          <el-card shadow="never">
            <MdPreview v-if="file_content" :model-value="file_content" noImgZoomIn />
            <template v-else>-</template>
          </el-card>
        </template>
      </div>
    </div>
  </DetailContainer>
</template>
