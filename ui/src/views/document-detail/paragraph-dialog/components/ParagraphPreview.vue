<script setup lang="ts">
import type { ParagraphDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { getFileUrl } from '@/utils/common'

defineOptions({ name: 'ParagraphPreview' })
defineProps<{ paragraph?: ParagraphDetail }>()
</script>

<template>
  <el-scrollbar height="100%" class="min-h-0 flex-1">
    <!-- 点击预览原图 -->
    <el-image
      v-if="paragraph?.source_file_id"
      class="w-fit [&_img]:size-auto! [&_img]:max-h-50 mb-2"
      :src="getFileUrl(paragraph.source_file_id)"
      :preview-src-list="[getFileUrl(paragraph.source_file_id)]"
      preview-teleported
      :scale="0.8"
      :alt="paragraph.title || ''"
      fit="contain"
    />
    <h4 class="mb-3 min-w-0 shrink-0 break-words">{{ paragraph?.title || '-' }}</h4>
    <MdPreview :model-value="paragraph?.content ?? ''" />
  </el-scrollbar>
  <div class="mt-4 flex-align-center shrink-0 gap-2 text-sm text-N600">
    <span>召回次数 {{ paragraph?.hit_num ?? 0 }}</span>
    <el-divider direction="vertical" />
    <span>最近一次召回时间 {{ datetimeFormat(paragraph?.last_hit_time) || '-' }}</span>
  </div>
</template>
