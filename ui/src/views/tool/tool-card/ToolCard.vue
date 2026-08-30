<script setup lang="ts">
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ToolStoreResponse } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import ToolStatusSwitch from './ToolStatusSwitch.vue'
import UpdateVersionButton from './UpdateVersionButton.vue'

defineOptions({ name: 'ToolCard' })

defineProps<{ api: typeof ToolApi; disabled?: boolean; selectable?: boolean; selected?: boolean; shared: boolean; storeTools: ToolStoreResponse['apps']; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ selected: [selected: boolean]; update: [tool: ToolItem] }>()

defineSlots<{ actions?: () => unknown; 'action-dropdown'?: () => unknown }>()
</script>

<template>
  <MkSourceCard
    :create_time="tool.create_time"
    :nick_name="tool.nick_name || '-'"
    :selectable="selectable"
    :selected="selected"
    :title="tool.name"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <ToolIcon :type="tool.tool_type" :icon="tool.icon" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
      <el-tag v-if="tool.version" size="small" type="info" effect="plain">
        {{ tool.version }}
      </el-tag>
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">共享</el-tag>
      <UpdateVersionButton v-else-if="!selectable" v-model:loading="loading" :store-tools="storeTools" :tool="tool" @update="emit('update', $event)" />
    </template>

    <p class="line-clamp-2" :title="tool.desc ?? undefined">
      {{ tool.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="tool.is_active" />
      <component :is="Action" v-if="!disabled">
        <ToolStatusSwitch v-model:loading="loading" :api="api" :tool="tool" @update="emit('update', $event)" />
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
