<script setup lang="ts">
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
import { computed } from 'vue'
import type { DocumentItem } from '@/api/types'

defineOptions({ name: 'DocumentTags' })
const props = defineProps<{ document: DocumentItem }>()
const emit = defineEmits<{ add: [documentId: string] }>()

// 优先使用接口数量，兼容只返回标签明细的数据。
const tagCount = computed(() => props.document.tag_count ?? props.document.tags?.length ?? 0)
</script>

<template>
  <div class="flex-align-center gap-1">
    <el-popover v-if="tagCount" trigger="hover" placement="bottom-start" width="auto" :show-after="TOOLTIP_SHOW_DELAY" :persistent="false">
      <template #reference>
        <el-tag type="info" effect="plain" class="shrink-0 cursor-pointer">
          <span class="flex-align-center gap-1 text-N900 py-1">
            <MkIcon name="icon_tag" />
            <!-- TODO tag字号 -->
            <span>{{ tagCount }}</span>
          </span>
        </el-tag>
      </template>
      <div class="py-2 px-3 max-w-210 space-y-1">
        <template v-for="tag in document.tags" :key="tag.id">
          <div class="flex-align-center gap-2">
            <span class="shrink-0 truncate text-N600" :title="tag.key">{{ tag.key }}</span>
            <span class="min-w-0 truncate" :title="tag.value">{{ tag.value }}</span>
          </div>
        </template>
      </div>
    </el-popover>
    <!-- 添加文档标签 -->
    <el-button class="mk-add-tag-button" plain @click.stop="emit('add', document.id)">
      <MkIcon name="icon_add_outlined" size="14" />
      <span>标签</span>
    </el-button>
  </div>
</template>
