<script setup lang="ts">
import { ref } from 'vue'
import MkFilterableDropdown from '@/components/mk-filterable-dropdown/index.vue'
import { ArrowDown, Collection } from '@element-plus/icons-vue'

/**
 * 工作空间下拉框。
 * 负责加载工作空间数据、维护当前工作空间，并组合通用的筛选下拉组件。
 */
defineOptions({ name: 'WorkspaceDropdown' })

/** 当前选中的工作空间 */
const selectedWorkspace = ref<string | number>('maxkb')
/** 工作空间列表；后续由工作空间接口返回 */
const workspaceOptions = [
  {
    label: 'MaxKB 工作空间工作空间',
    value: 'maxkb-default',
  },
  { label: 'MaxKB 工作空间', value: 'maxkb' },
  { label: 'MaxKB 工作空间 1', value: 'maxkb-1' },
  { label: 'MaxKB 工作空间 2', value: 'maxkb-2' },
  { label: '工作空间名称比较长的展示效果如下', value: 'long-name' },
  { label: '研发工作空间', value: 'development' },
  { label: '测试工作空间', value: 'testing' },
]
</script>

<template>
  <MkFilterableDropdown
    v-model="selectedWorkspace"
    :options="workspaceOptions"
    placeholder="请选择工作空间"
  >
    <template #default="{ text }">
      <button type="button" class="flex max-w-50 items-center gap-1 rounded-md px-2 py-1">
        <MkIcon :icon="Collection" class="shrink-0" />
        <span class="min-w-0 flex-1 truncate">{{ text }}</span>
        <MkIcon :icon="ArrowDown" class="shrink-0" />
      </button>
    </template>

    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <MkIcon :icon="Collection" class="shrink-0" />
        <span class="min-w-0 flex-1 truncate">{{ option.label }}</span>
      </div>
    </template>
  </MkFilterableDropdown>
</template>
