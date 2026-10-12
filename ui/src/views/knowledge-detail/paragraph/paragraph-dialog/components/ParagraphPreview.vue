<script setup lang="ts">
import { EditPen } from '@element-plus/icons-vue'
import type { ParagraphDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'ParagraphPreview' })
const props = withDefaults(defineProps<{ paragraph?: ParagraphDetail; disabled?: boolean; loading?: boolean }>(), {
  disabled: false,
  loading: false,
})
const emit = defineEmits<{ edit: [] }>()

function handleEdit() {
  if (!props.disabled && !props.loading) emit('edit')
}
</script>

<template>
  <div class="mk-gray-card-lg flex-column min-h-0 max-h-[calc(100vh-272px)] min-w-0 flex-1 border">
    <div class="mb-3 flex-between shrink-0 gap-3">
      <h4 class="min-w-0 break-words">{{ paragraph?.title || '无标题分段' }}</h4>
      <!-- 编辑分段标题和内容 -->
      <el-button circle class="shrink-0 shadow-sm" title="编辑分段" v-if="!disabled" :disabled="loading" @click="handleEdit">
        <MkIcon :icon="EditPen" :size="18" />
      </el-button>
    </div>
    <el-scrollbar class="min-h-0 flex-1">
      <MdPreview :model-value="paragraph?.content ?? ''" />
    </el-scrollbar>
    <div class="mt-4 flex-align-center shrink-0 flex-wrap gap-x-2 text-sm text-N600">
      <span>召回次数 {{ paragraph?.hit_num ?? 0 }}</span>
      <el-divider direction="vertical" />
      <span>最近一次召回时间 {{ datetimeFormat(paragraph?.last_hit_time) || '暂无' }}</span>
    </div>
  </div>
</template>
