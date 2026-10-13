<script setup lang="ts">
import type { ParagraphDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'ParagraphPreview' })
defineProps<{ paragraph?: ParagraphDetail }>()
</script>

<template>
  <h4 class="mb-3 min-w-0 shrink-0 break-words">{{ paragraph?.title || '-' }}</h4>
  <el-scrollbar height="100%" class="min-h-0 flex-1">
    <MdPreview :model-value="paragraph?.content ?? ''" />
  </el-scrollbar>
  <div class="mt-4 flex-align-center shrink-0 gap-2 text-sm font-medium text-N600">
    <span>召回次数 {{ paragraph?.hit_num ?? 0 }}</span>
    <el-divider direction="vertical" />
    <span>最近一次召回时间 {{ datetimeFormat(paragraph?.last_hit_time) || '-' }}</span>
  </div>
</template>
