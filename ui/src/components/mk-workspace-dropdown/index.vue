<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import type { OptionItem } from '@/api/types'

defineOptions({ name: 'MkWorkspaceDropdown' })

const props = defineProps<{
  options: OptionItem[]
}>()
const selectedWorkspace = defineModel<string | number>({ required: true })
const emit = defineEmits<{
  select: [option: OptionItem]
}>()
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspace"
    :options="props.options"
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
        <span class="min-w-0 flex-1 truncate">{{ option.label }}</span>
      </div>
    </template>
  </MkFilterableDropdown>
</template>
