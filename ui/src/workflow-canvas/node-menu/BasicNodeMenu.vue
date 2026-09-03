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
  <div class="p-4">
    <MkSearchInput v-model="searchKeyword" placeholder="按名称搜索" />

    <el-scrollbar height="450" class="mk-scrollbar-right">
      <template v-if="filteredComponentGroups.length">
        <template v-for="group in filteredComponentGroups" :key="group.label">
          <p class="mb-3 mt-3 font-semibold text-sm text-N600">{{ group.label }}</p>
          <div class="grid grid-cols-2 gap-3">
            <template v-for="workflowNode in group.list" :key="workflowNode.type">
              <el-card
                class="small cursor-pointer"
                shadow="never"
                @click="emit('select', workflowNode)"
                @pointerdown="handleNodeDragStart($event, workflowNode)"
              >
                <div class="flex items-center gap-2">
                  <component :is="iconComponent(`${workflowNode.type}-icon`)" :size="20" />
                  <span>{{ workflowNode.label }}</span>
                </div>
              </el-card>
            </template>
          </div>
        </template>
      </template>
      <MkEmpty v-else type="search" />
    </el-scrollbar>
  </div>
</template>
