<script setup lang="ts">
import type { ProblemParagraph } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'ProblemParagraphCard' })
defineProps<{ paragraph: ProblemParagraph; disabled?: boolean }>()
const emit = defineEmits<{ open: [paragraph: ProblemParagraph]; unlink: [paragraph: ProblemParagraph] }>()
</script>

<template>
  <!-- 查看关联分段详情 -->
  <el-card class="mk-paragraph-card group relative cursor-pointer" shadow="never" @click="!disabled && emit('open', paragraph)">
    <h4 class="mb-2 truncate pr-8" :title="paragraph.title || '-'">{{ paragraph.title || '-' }}</h4>
    <p class="mb-3 line-clamp-2 break-words" :title="paragraph.content">{{ paragraph.content }}</p>
    <div class="flex-align-center gap-2 text-sm text-N500">
      <span class="shrink-0">{{ paragraph.content.length }} 字符</span>
      <el-divider direction="vertical" />
      <img :src="getFileIconUrl(paragraph.document_name)" class="size-4 shrink-0" alt="" />
      <span class="truncate" :title="paragraph.document_name">{{ paragraph.document_name }}</span>
    </div>
    <!-- 取消当前问题与分段的关联，不删除分段 -->
    <MkTooltip content="取消关联" placement="top">
      <el-button circle class="group-hover-visible absolute top-3 right-3 shadow-md" :disabled="disabled" @click.stop="emit('unlink', paragraph)">
        <MkIcon name="icon_unlink_outlined" />
      </el-button>
    </MkTooltip>
  </el-card>
</template>
