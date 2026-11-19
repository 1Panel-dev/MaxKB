<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { NodeMenuItem, NodeMenuTab } from './types'
import { RESOURCE_TYPE } from '@/api/enums'
import { WorkflowMode } from '@/workflow-canvas/types'
import BasicNodeMenu from './BasicNodeMenu.vue'
import ResourceNodeMenu from './ResourceNodeMenu.vue'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'NodeMenu' })

defineProps<{
  workflowMode: WorkflowMode
}>()

const emit = defineEmits<{
  dragstart: [node: NodeMenuItem, event: PointerEvent]
  select: [node: NodeMenuItem]
}>()

const activeTab = ref<NodeMenuTab>('basic')

function handleDragStart(node: NodeMenuItem, event: PointerEvent) {
  emit('dragstart', node, event)
}
</script>

<template>
  <div
    class="overflow-hidden rounded-xl border bg-white shadow-md"
    :class="activeTab === 'basic' ? 'w-[414px]' : 'w-[670px]'"
    @click.stop
    @mousedown.stop
    @mousemove.stop
  >
    <el-tabs v-model="activeTab" class="small p-4 pb-0">
      <el-tab-pane :label="t('workflow.menu.basicComponents')" name="basic" />
      <el-tab-pane
        :label="t('resource.dataSource.label')"
        name="data-source"
        v-if="workflowMode === WorkflowMode.Knowledge || workflowMode === WorkflowMode.KnowledgeLoop"
      />
      <el-tab-pane :label="t('tool.title')" name="tool" />
      <el-tab-pane
        :label="t('application.title')"
        name="application"
        v-if="workflowMode === WorkflowMode.Application || workflowMode === WorkflowMode.ApplicationLoop"
      />
    </el-tabs>

    <KeepAlive>
      <BasicNodeMenu v-if="activeTab === 'basic'" :workflow-mode="workflowMode" @dragstart="handleDragStart" @select="emit('select', $event)" />

      <ResourceNodeMenu
        v-else
        :key="activeTab"
        :source="activeTab === 'application' ? RESOURCE_TYPE.APPLICATION : RESOURCE_TYPE.TOOL"
        :data-source="activeTab === 'data-source'"
        @dragstart="handleDragStart"
        @select="emit('select', $event)"
      />
    </KeepAlive>
  </div>
</template>

<style lang="scss" scoped></style>
