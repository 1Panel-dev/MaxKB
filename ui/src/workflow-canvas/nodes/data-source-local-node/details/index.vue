<script setup lang="ts">
import { computed } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { downloadByURL, getFileUrl } from '@/utils/common'
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
          <!-- 下载来源文件 -->
          <el-card
            shadow="never"
            class="small min-w-0"
            :class="{ 'cursor-pointer': file.file_id }"
            @click="file.file_id && downloadByURL(getFileUrl(file.file_id), file.name || '')"
          >
            <div class="flex-align-center gap-2">
              <img :src="getFileIconUrl(file.name || '')" alt="" width="24" />
              <span class="min-w-0 truncate" :title="file.name">{{ file.name || '-' }}</span>
            </div>
          </el-card>
        </template>
      </div>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
