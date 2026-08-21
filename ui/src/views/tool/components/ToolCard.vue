<script setup lang="ts">
import type { ToolItem } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'ToolCard' })

const props = defineProps<{
  shared: boolean
  tool: ToolItem
}>()

const emit = defineEmits<{
  delete: [tool: ToolItem]
  select: [tool: ToolItem]
  statusChange: [tool: ToolItem, active: boolean]
}>()

function handleStatusChange(active: string | number | boolean) {
  emit('statusChange', props.tool, Boolean(active))
}
</script>

<template>
  <MkSourceCard
    :create_time="tool.create_time"
    :nick_name="tool.nick_name || '-'"
    :title="tool.name"
  >
    <template #icon>
      <ToolIcon :type="tool?.tool_type" :icon="tool.icon" />
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info" class="text-N600!">共享</el-tag>
    </template>

    <p class="line-clamp-2" :title="tool?.desc ?? undefined">
      {{ tool.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="tool.is_active" />
      <component :is="Action" v-if="!shared">
        <el-switch
          :model-value="tool.is_active"
          class="mr-1"
          size="small"
          @change="handleStatusChange"
        />
        <el-divider direction="vertical" />
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
