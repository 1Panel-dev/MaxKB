<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowMenuNode } from '@/workflow-canvas/node-menu/menu'
import type { WorkflowMode } from '@/workflow-canvas/types'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import { WORKFLOW_MENU_LABELS, WORKFLOW_NODE_DISPLAY, getMenuNodes } from '@/workflow-canvas/node-menu/menu'

const { t } = useI18n({ useScope: 'global' })

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
    .map((group) => ({
      ...group,
      list: group.list.filter((node) => (WORKFLOW_NODE_DISPLAY[node.type]?.label ?? node.label).toLocaleLowerCase().includes(keyword)),
    }))
    .filter((group) => group.list.length > 0)
})

function handleNodeDragStart(event: PointerEvent, workflowNode: WorkflowMenuNode) {
  if (event.button === 0) emit('dragstart', workflowNode, event)
}
</script>

<template>
  <div class="p-4">
    <MkSearchInput v-model="searchKeyword" :placeholder="t('workflow.menu.searchPlaceholder')" />

    <el-scrollbar height="450" class="mk-scrollbar-right">
      <template v-if="filteredComponentGroups.length">
        <template v-for="group in filteredComponentGroups" :key="group.label">
          <p class="mb-3 mt-3 font-semibold text-sm text-N600">{{ WORKFLOW_MENU_LABELS[group.label] ?? group.label }}</p>
          <div class="grid grid-cols-2 gap-3">
            <template v-for="workflowNode in group.list" :key="workflowNode.type">
              <el-popover placement="right" :width="280" :show-after="TOOLTIP_SHOW_DELAY" :persistent="false">
                <template #reference>
                  <!-- 点击或拖拽添加节点 -->
                  <el-card
                    class="small cursor-pointer hover:border-primary!"
                    shadow="never"
                    @click="emit('select', workflowNode)"
                    @pointerdown="handleNodeDragStart($event, workflowNode)"
                  >
                    <div class="flex-align-center gap-2">
                      <component :is="iconComponent(`${workflowNode.type}-icon`)" :size="20" />
                      <span>{{ WORKFLOW_NODE_DISPLAY[workflowNode.type]?.label ?? workflowNode.label }}</span>
                    </div>
                  </el-card>
                </template>
                <div class="p-3">
                  <div class="flex-align-center min-w-0 gap-2">
                    <component :is="iconComponent(`${workflowNode.type}-icon`)" :size="24" />
                    <p class="min-w-0 flex-1 break-all truncate">{{ WORKFLOW_NODE_DISPLAY[workflowNode.type]?.label ?? workflowNode.label }}</p>
                  </div>
                  <p v-if="workflowNode.text" class="mt-2 text-sm text-N600">
                    {{ WORKFLOW_NODE_DISPLAY[workflowNode.type]?.description ?? workflowNode.text }}
                  </p>
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
