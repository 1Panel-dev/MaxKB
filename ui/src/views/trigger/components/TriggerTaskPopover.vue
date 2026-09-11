<script setup lang="ts">
import { computed } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import type { TriggerTask } from '@/api/types'

const props = withDefaults(defineProps<{ tasks?: TriggerTask[] }>(), { tasks: () => [] })

const taskGroups = computed(() =>
  [
    { type: RESOURCE_TYPE.APPLICATION, label: '智能体' },
    { type: RESOURCE_TYPE.TOOL, label: '工具' },
  ]
    .map((group) => ({ ...group, tasks: props.tasks.filter((task) => task.type === group.type) }))
    .filter((group) => group.tasks.length > 0),
)
</script>

<template>
  <el-popover v-if="taskGroups.length" placement="bottom-start" :width="240" popper-class="p-0!" :show-arrow="false" :persistent="false">
    <template #reference>
      <div class="inline-flex items-center gap-2">
        <el-tag v-for="group in taskGroups" :key="group.type" size="small" type="info" class="cursor-pointer">
          {{ group.label }} {{ group.tasks.length }}
        </el-tag>
      </div>
    </template>

    <el-scrollbar max-height="320px">
      <div v-for="(group, groupIndex) in taskGroups" :key="group.type" class="px-3 py-2" :class="{ 'border-t': groupIndex > 0 }">
        <p class="mb-2 text-N500">{{ group.label }}</p>
        <div v-for="(task, taskIndex) in group.tasks" :key="taskIndex" class="flex h-8 items-center gap-2 text-N900">
          <ApplicationIcon v-if="group.type === RESOURCE_TYPE.APPLICATION" :icon="task.icon ?? undefined" :size="20" class="shrink-0" />
          <ToolIcon v-else :icon="task.icon ?? undefined" :size="20" class="shrink-0" />
          <span class="truncate" :title="task.name || '-'">{{ task.name || '-' }}</span>
        </div>
      </div>
    </el-scrollbar>
  </el-popover>
  <span v-else>-</span>
</template>
