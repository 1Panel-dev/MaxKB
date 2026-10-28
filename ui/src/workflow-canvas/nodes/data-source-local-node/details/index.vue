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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">文件列表</h6>
      <div v-if="fileList.length > 0" class="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <template v-for="(file, index) in fileList" :key="file.file_id || index">
          <!-- 在新标签页打开或下载文件 -->
          <a
            :href="file.file_id ? getFileUrl(file.file_id) : undefined"
            target="_blank"
            rel="noopener noreferrer"
            :download="file.name"
            class="block min-w-0"
          >
            <el-card shadow="never" class="small" :class="{ 'cursor-pointer': file.file_id }">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(file.name || '')" alt="" width="24" />
                <span class="min-w-0 truncate" :title="file.name">{{ file.name || '-' }}</span>
              </div>
            </el-card>
          </a>
        </template>
      </div>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
