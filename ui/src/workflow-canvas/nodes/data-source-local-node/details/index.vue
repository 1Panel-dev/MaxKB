<script setup lang="ts">
import { computed } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'DataSourceLocalNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface SourceFile {
  file_id?: string
  name?: string
}

const fileList = computed<SourceFile[]>(() => (props.data?.file_list as SourceFile[] | undefined) || [])
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">文件列表</h6>
      <div class="space-y-2">
        <template v-if="fileList.length > 0">
          <div
            v-for="(file, index) in fileList"
            :key="file.file_id || index"
            class="mb-2 flex-align-center gap-1 overflow-hidden rounded-md bg-white p-2 last:mb-0"
          >
            <img :src="getFileIconUrl(file.name || '')" alt="" width="20" />
            <a v-if="file.file_id" :href="getFileUrl(file.file_id)" target="_blank" class="truncate" :title="file.name">
              {{ file.name }}
            </a>
            <span v-else class="truncate" :title="file.name">{{ file.name || '-' }}</span>
          </div>
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
