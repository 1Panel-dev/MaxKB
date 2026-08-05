<script setup lang="ts" generic="Option extends DropdownOption = DropdownOption">
import { CaretBottom } from '@element-plus/icons-vue'
import type { DropdownOption } from '@/components/global/mk-filterable-dropdown/types'

defineOptions({ name: 'MkWorkspaceDropdown' })

const props = defineProps<{
  options: Option[]
}>()
const selectedWorkspace = defineModel<string | number>({ required: true })
const emit = defineEmits<{
  select: [option: Option]
}>()
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspace"
    :options="props.options"
    placeholder="请选择工作空间"
    @select="emit('select', $event)"
  >
    <template #default="{ text }">
      <el-button text class="flex max-w-50 items-center gap-1 rounded-md px-2! py-[7px]!">
        <MkIcon name="icon_moments-categories_outlined" class="mr-1"/>
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
