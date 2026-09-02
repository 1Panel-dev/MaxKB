<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { getMenuNodes, type WorkflowMenuNode } from '@/workflow-canvas/node-menu/menu'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'BasicNodeMenu' })

const emit = defineEmits<{
  dragstart: [workflowNode: WorkflowMenuNode, event: PointerEvent]
  select: [workflowNode: WorkflowMenuNode]
}>()

const searchKeyword = ref('')
const workflowMode = inject('workflowMode', WorkflowMode.Application)
const workflowComponentGroups = computed(() => getMenuNodes(workflowMode) ?? [])

const filteredComponentGroups = computed(() => {
  const keyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!keyword) return workflowComponentGroups.value

  return workflowComponentGroups.value
    .map((group) => ({ ...group, list: group.list.filter((node) => node.label.toLocaleLowerCase().includes(keyword)) }))
    .filter((group) => group.list.length > 0)
})

function handleNodeDragStart(event: PointerEvent, workflowNode: WorkflowMenuNode) {
  if (event.button === 0) emit('dragstart', workflowNode, event)
}
</script>

<template>
  <div>
    <MkSearchInput v-model="searchKeyword" placeholder="按名称搜索" />

    <el-scrollbar height="500">
      <template v-if="filteredComponentGroups.length">
        <template v-for="group in filteredComponentGroups" :key="group.label">
          <p class="mb-3 mt-3 text-N600">{{ group.label }}</p>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="workflowNode in group.list"
              :key="workflowNode.type"
              type="button"
              class="flex h-10 cursor-grab items-center gap-3 rounded-md border border-N300 px-3 text-left text-N900 hover:border-primary hover:text-primary active:cursor-grabbing"
              @click="emit('select', workflowNode)"
              @pointerdown="handleNodeDragStart($event, workflowNode)"
            >
              <component :is="iconComponent(`${workflowNode.type}-icon`)" class="shrink-0" :size="24" />
              <span>{{ workflowNode.label }}</span>
            </button>
          </div>
        </template>
      </template>
      <MkEmpty v-else type="search" />
    </el-scrollbar>
  </div>
</template>
