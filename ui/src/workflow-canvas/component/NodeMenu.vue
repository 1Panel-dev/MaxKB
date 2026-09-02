<script setup lang="ts">
import { computed, inject, ref } from 'vue'

import { getMenuNodes, type WorkflowMenuNode } from '@/workflow-canvas/config/menu'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'NodeMenu' })

const emit = defineEmits<{
  dragstart: [workflowNode: WorkflowMenuNode, event: PointerEvent]
  select: [workflowNode: WorkflowMenuNode]
}>()

type WorkflowComponentTab = 'basic' | 'tool' | 'application'

const activeTab = ref<WorkflowComponentTab>('basic')
const searchKeyword = ref('')
const workflowMode = inject('workflowMode', WorkflowMode.Application)

const workflowComponentTabs: Array<{ label: string; value: WorkflowComponentTab }> = [
  { label: '基础组件', value: 'basic' },
  { label: '工具', value: 'tool' },
  { label: '智能体', value: 'application' },
]

const workflowComponentGroups = computed(() => getMenuNodes(workflowMode) ?? [])

const filteredComponentGroups = computed(() => {
  if (activeTab.value !== 'basic') return []

  const keyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!keyword) return workflowComponentGroups.value

  return workflowComponentGroups.value
    .map((group) => ({ ...group, list: group.list.filter((node) => node.label.toLocaleLowerCase().includes(keyword)) }))
    .filter((group) => group.list.length > 0)
})

const handleNodeDragStart = (event: PointerEvent, workflowNode: WorkflowMenuNode) => {
  if (event.button === 0) emit('dragstart', workflowNode, event)
}
</script>

<template>
  <div class="w-[402px] overflow-hidden rounded-md border border-N300 bg-white shadow-lg" @click.stop @mousedown.stop @mousemove.stop>
    <div class="flex h-11 items-stretch gap-7 border-b border-N300 px-4" role="tablist">
      <button
        v-for="componentTab in workflowComponentTabs"
        :key="componentTab.value"
        type="button"
        role="tab"
        class="relative font-medium"
        :class="activeTab === componentTab.value ? 'text-primary' : 'text-N900'"
        :aria-selected="activeTab === componentTab.value"
        @click="activeTab = componentTab.value"
      >
        {{ componentTab.label }}
        <span v-if="activeTab === componentTab.value" class="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-primary" />
      </button>
    </div>

    <div class="p-3">
      <MkSearchInput v-model="searchKeyword" placeholder="按名称搜索" />

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
      <MkEmpty v-else :type="searchKeyword ? 'search' : 'default'" :image-size="72" />
    </div>
  </div>
</template>
