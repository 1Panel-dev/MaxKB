<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import type { WorkspaceItem } from '@/api/types'

defineOptions({ name: 'WorkspaceDropdown' })

const props = defineProps<{ options: WorkspaceItem[] }>()
const selectedWorkspaceId = defineModel<string>({ required: true })
const emit = defineEmits<{ select: [option: WorkspaceItem] }>()
</script>

<template>
  <MkFilterableDropdown v-model="selectedWorkspaceId" :options="props.options" :props="{ label: 'name', value: 'id' }" @select="emit('select', $event)">
    <template #default="{ text }">
      <el-button text class="flex max-w-50 items-center gap-1 rounded-md px-2! py-[7px]! text-N900!">
        <MkIcon name="icon_moments-categories_outlined" class="mr-1" />
        <span class="min-w-0 flex-1 truncate" :title="text">{{ text }}</span>
        <MkIcon :icon="CaretBottom" :size="14" class="ml-1 shrink-0 text-N600!" />
      </el-button>
    </template>

    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <MkIcon name="icon_moments-categories_outlined" />
        <span class="min-w-0 flex-1 truncate" :title="option.name">{{ option.name }}</span>
      </div>
    </template>
  </MkFilterableDropdown>
</template>
