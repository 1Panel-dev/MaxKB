<script setup lang="ts">
import { computed } from 'vue'
import { Download } from '@element-plus/icons-vue'
import type { ToolStoreItem } from '@/api/types'
import { numberFormat } from '@/utils/number'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'ToolStoreCard' })

const props = defineProps<{
  categoryTitle: string
  loading: boolean
  tool: ToolStoreItem
}>()

const emit = defineEmits<{
  add: []
  detail: []
}>()

const toolTypeLabel = computed(() => (props.tool.label === 'data_source' ? '数据源' : '工具'))
</script>

<template>
  <MkSourceCard :title="tool.name" class="hover:border-primary! focus-within:border-primary!">
    <template #icon>
      <ToolIcon :icon="tool.icon" :size="32" :type="tool.tool_type" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
      <el-tag v-if="tool.version" size="small" type="info">{{ tool.version }}</el-tag>
    </template>
    <template #subtitle>{{ categoryTitle }}</template>
    <template #tag>
      <el-tag size="small" type="info">{{ toolTypeLabel }}</el-tag>
    </template>

    <p class="line-clamp-2" :title="tool.desc ?? undefined">{{ tool.desc || '-' }}</p>

    <template #footer>
      <span
        class="flex items-center gap-1 text-sm text-N600 group-hover:hidden group-focus-within:hidden"
      >
        <MkIcon v-if="tool.downloads !== undefined" :icon="Download" />
        {{
          tool.downloads === undefined
            ? tool.source === 'internal'
              ? '系统内置'
              : '工具商店'
            : numberFormat(tool.downloads)
        }}
      </span>
      <div class="group-hover-visible flex min-w-0 flex-1 gap-2" @click.stop>
        <el-button class="flex-1!" plain @click="emit('detail')">详情</el-button>
        <el-button class="flex-1!" type="primary" :loading="loading" @click="emit('add')">
          添加
        </el-button>
      </div>
    </template>
  </MkSourceCard>
</template>
