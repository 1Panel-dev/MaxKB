<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import type { WorkspaceItem } from '@/api/types'

defineOptions({ name: 'MkWorkspaceDropdown' })

/*  此组件专属为工作空间 dropdown 使用，图标（icon_moments-categories_outlined）已硬编码。
     若其他场景需要替换图标，后续应完善 props，将图标作为可配置参数传入。*/

const props = defineProps<{
  options: WorkspaceItem[]
}>()
const selectedWorkspaceId = defineModel<string>({ required: true })
const emit = defineEmits<{
  select: [option: WorkspaceItem]
}>()
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspaceId"
    :options="props.options"
    :props="{ label: 'name', value: 'id' }"
    @select="emit('select', $event)"
  >
    <template #default="{ text }">
      <el-button text class="flex max-w-50 items-center gap-1 rounded-md px-2! py-[7px]!">
        <MkIcon name="icon_moments-categories_outlined" class="mr-1" />
        <span class="min-w-0 flex-1 truncate">{{ text }}</span>
        <MkIcon :icon="CaretBottom" :size="14" class="shrink-0 ml-1 text-N600!" />
      </el-button>
    </template>

    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <MkIcon name="icon_moments-categories_outlined" />
        <span class="min-w-0 flex-1 truncate">{{ option.name }}</span>
      </div>
    </template>
  </MkFilterableDropdown>
</template>
