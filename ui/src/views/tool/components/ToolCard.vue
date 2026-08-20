<script setup lang="ts">
import { computed, type Component } from 'vue'
import { Box, Coin, Connection, MagicStick } from '@element-plus/icons-vue'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolType, WorkspaceTool } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'ToolCard' })

const props = defineProps<{
  selected: boolean
  shared: boolean
  tool: WorkspaceTool
}>()

const emit = defineEmits<{
  delete: [tool: WorkspaceTool]
  select: [tool: WorkspaceTool]
  statusChange: [tool: WorkspaceTool, active: boolean]
}>()

const TOOL_TYPE_LABELS: Record<ToolType, string> = {
  [TOOL_TYPE.CUSTOM]: '工具',
  [TOOL_TYPE.DATA_SOURCE]: '数据源',
  [TOOL_TYPE.INTERNAL]: '内置工具',
  [TOOL_TYPE.MCP]: 'MCP',
  [TOOL_TYPE.SKILL]: 'Skills',
  [TOOL_TYPE.WORKFLOW]: '工作流',
}

const TOOL_TYPE_ICONS: Record<ToolType, Component> = {
  [TOOL_TYPE.CUSTOM]: Box,
  [TOOL_TYPE.DATA_SOURCE]: Coin,
  [TOOL_TYPE.INTERNAL]: Box,
  [TOOL_TYPE.MCP]: Connection,
  [TOOL_TYPE.SKILL]: MagicStick,
  [TOOL_TYPE.WORKFLOW]: Connection,
}

const toolDescription = computed(() => props.tool.desc || TOOL_TYPE_LABELS[props.tool.tool_type])
const isInlineSvg = computed(() => props.tool.icon?.trim().startsWith('<svg'))

function handleStatusChange(active: string | number | boolean) {
  emit('statusChange', props.tool, Boolean(active))
}
</script>

<template>
  <MkSourceCard
    :class="{ 'is-selected': selected }"
    :create_time="tool.create_time"
    :nick_name="tool.nick_name || '-'"
    :title="tool.name"
    class="tool-card cursor-pointer"
    @click="emit('select', tool)"
  >
    <template #icon>
      <span
        v-if="tool.icon && isInlineSvg"
        class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg [&>svg]:h-full [&>svg]:w-full"
        v-html="tool.icon"
      />
      <img
        v-else-if="tool.icon"
        :alt="tool.name"
        :src="tool.icon"
        class="h-8 w-8 rounded-lg object-cover"
      />
      <span
        v-else
        class="flex h-8 w-8 items-center justify-center rounded-lg"
        :class="tool.tool_type === TOOL_TYPE.SKILL ? 'bg-primary' : 'bg-success'"
      >
        <MkIcon :icon="TOOL_TYPE_ICONS[tool.tool_type]" :size="18" class="text-white!" />
      </span>
    </template>

    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
      <el-tag v-if="tool.version" size="small" type="info" effect="plain">
        {{ tool.version }}
      </el-tag>
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info" class="text-N600!">共享</el-tag>
    </template>

    <p class="line-clamp-2 min-h-11 text-N600" :title="toolDescription">
      {{ toolDescription }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="tool.is_active" />
      <component :is="Action" v-if="!shared">
        <el-switch :model-value="tool.is_active" size="small" @change="handleStatusChange" />
        <component :is="ActionDropdown">
          <MkDropdownMenu>
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_edit_outlined" /></template>
              <span>编辑</span>
            </MkDropdownItem>
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_assigned_outlined" /></template>
              <span>资源授权</span>
            </MkDropdownItem>
            <MkDropdownItem divided @click="emit('delete', tool)">
              <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>

<style lang="scss" scoped></style>
