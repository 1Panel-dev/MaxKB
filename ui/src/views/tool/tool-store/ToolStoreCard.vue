<script setup lang="ts">
import { computed } from 'vue'
import type { ToolStoreItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
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

const toolTypeLabel = computed(() => {
  const typeLabels = {
    [TOOL_TYPE.CUSTOM]: '自定义工具',
    [TOOL_TYPE.DATA_SOURCE]: '数据源',
    [TOOL_TYPE.INTERNAL]: '内置工具',
    [TOOL_TYPE.MCP]: 'MCP',
    [TOOL_TYPE.SKILL]: 'Skill',
    [TOOL_TYPE.WORKFLOW]: '工作流',
  }
  return typeLabels[props.tool.tool_type]
})
</script>

<template>
  <MkSourceCard :title="tool.name">
    <!-- //TODO 暂时不提供click事件，先把编辑逻辑捋好。复用过来 -->
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
      <span class="text-sm text-N600">
        {{
          tool.downloads === undefined
            ? tool.source === 'internal'
              ? '系统内置'
              : '工具商店'
            : `下载 ${numberFormat(tool.downloads)}`
        }}
      </span>
      <div class="ml-auto flex gap-2" @click.stop>
        <el-button plain @click="emit('detail')">详情</el-button>
        <el-button type="primary" :loading="loading" @click="emit('add')">添加</el-button>
      </div>
    </template>
  </MkSourceCard>
</template>
