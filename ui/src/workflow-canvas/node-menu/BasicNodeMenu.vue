<script setup lang="ts">
import { computed, ref } from 'vue'
import { getMenuNodes, type WorkflowMenuNode } from '@/workflow-canvas/node-menu/menu'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import type { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'BasicNodeMenu' })

const emit = defineEmits<{
  dragstart: [workflowNode: WorkflowMenuNode, event: PointerEvent]
  select: [workflowNode: WorkflowMenuNode]
}>()
const props = defineProps<{ workflowMode: WorkflowMode }>()

const searchKeyword = ref('')
const workflowComponentGroups = computed(() => getMenuNodes(props.workflowMode))

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
              <el-popover placement="right" :width="280" :show-after="500" :persistent="false">
                <template #reference>
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
                <div class="p-3">
                  <div class="flex min-w-0 items-center gap-2">
                    <component :is="iconComponent(`${workflowNode.type}-icon`)" :size="24" />
                    <p class="min-w-0 flex-1 break-all truncate">{{ workflowNode.label }}</p>
                  </div>
                  <p v-if="workflowNode.text" class="mt-2 text-sm text-N600">{{ workflowNode.text }}</p>
                </div>
              </el-popover>
            </template>
          </div>
        </template>
      </template>
      <MkEmpty v-else type="search" />
    </el-scrollbar>
  </div>
</template>
