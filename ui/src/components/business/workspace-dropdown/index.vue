<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import type { WorkspaceItem } from '@/api/types'
import MkFilterableDropdown from '@/components/mk-filterable-dropdown/index.vue'

defineOptions({ name: 'WorkspaceDropdown' })

const props = withDefaults(
  defineProps<{
    options: WorkspaceItem[]
    /** 是否显示工作空间角色标签 */
    showRoleTags?: boolean
  }>(),
  { showRoleTags: false },
)
const selectedWorkspaceId = defineModel<string>({ required: true })
const emit = defineEmits<{ select: [option: WorkspaceItem] }>()
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspaceId"
    :options="props.options"
    :props="{ label: 'name', value: 'id' }"
    @select="emit('select', $event)"
  >
    <template #default="{ text }">
      <!-- 切换工作空间 -->
      <el-button text class="flex max-w-50 items-center gap-1 rounded-md px-2! py-[7px]! text-N900!">
        <MkIcon name="icon_moments-categories_outlined" class="mr-1" />
        <span class="min-w-0 flex-1 truncate" :title="text">{{ text }}</span>
        <MkIcon :icon="CaretBottom" :size="14" class="ml-1 text-N600!" />
      </el-button>
    </template>

    <template #option="{ option }">
      <div class="flex min-w-0 flex-1 items-center gap-2">
        <MkIcon name="icon_moments-categories_outlined" class="shrink-0" />
        <span class="min-w-0 truncate" :title="option.name">{{ option.name }}</span>
        <MkTagGroup v-if="props.showRoleTags && option.role_name?.length" :tags="option.role_name" size="small" class="min-w-0 shrink-0" />
      </div>
    </template>
  </MkFilterableDropdown>
</template>

<style scoped lang="scss"></style>
