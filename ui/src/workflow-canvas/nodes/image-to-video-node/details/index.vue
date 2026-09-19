<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ImageToVideoNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" show-tokens />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">本次对话</h6>
      <div class="whitespace-pre-wrap">
        {{ data.question || '-' }}
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">负向提示词</h6>
      <div class="whitespace-pre-wrap">
        {{ data.negative_prompt || '-' }}
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">首帧</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <el-image
          v-if="typeof data.first_frame_url === 'string'"
          :src="data.first_frame_url"
          fit="cover"
          class="block h-10 w-10 rounded-md"
          :zoom-rate="1.2"
          :max-scale="7"
          :min-scale="0.2"
        />
        <div v-else-if="Array.isArray(data.first_frame_url)" class="flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.first_frame_url"
            :key="i"
            :src="f.url"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.first_frame_url.map((img: any) => img.url)"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
          />
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">末帧</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <el-image
          v-if="typeof data.last_frame_url === 'string'"
          :src="data.last_frame_url"
          fit="cover"
          class="block h-10 w-10 rounded-md"
          :zoom-rate="1.2"
          :max-scale="7"
          :min-scale="0.2"
        />
        <div v-else-if="Array.isArray(data.last_frame_url)" class="flex flex-wrap gap-2">
          <el-image
            v-for="(f, i) in data.last_frame_url"
            :key="i"
            :src="f.url"
            fit="cover"
            class="block h-10 w-10 rounded-md"
            :preview-src-list="data.last_frame_url.map((img: any) => img.url)"
            :initial-index="i"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
          />
        </div>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">AI 回答</h6>
      <div class="space-y-2">
        <MdPreview v-if="data.answer" :model-value="data.answer" noImgZoomIn />
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
