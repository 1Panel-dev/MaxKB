<template>
  <Draggable
    ref="treeRef"
    virtualization
    :defaultOpen="false"
    v-bind="$attrs"
    class="maxkb-virtualized-tree"
    @click:node="handleNodeClick"
    @after-drop="onAfterDrop"
    :rootDroppable="false"
    :statHandler="statHandler"
  >
    <template #default="{ node, stat }">
      <div
        class="flex align-center maxkb-tree-node"
        :class="currentNodeKey === node.id ? 'is-current' : ''"
      >
        <el-icon
          class="tree-arrow-icon"
          :class="stat.open ? 'rotate-90' : ''"
          :style="{ visibility: stat.children.length ? 'visible' : 'hidden' }"
        >
          <CaretRight />
        </el-icon>
        <div class="tree-label lighter">
          <slot name="default" v-bind="{ node, stat }">
            <span :title="node.name">{{ node.name }}</span>
          </slot>
        </div>
      </div>
    </template>
  </Draggable>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick } from 'vue'
import { Draggable, dragContext } from '@he-tree/vue'
import '@he-tree/vue/style/default.css'
const props = defineProps({
  currentNodeKey: {
    type: String,
    default: 'default',
  },
})

type DraggableInstance = InstanceType<typeof Draggable>
const treeRef = ref<DraggableInstance | null>(null)
const emit = defineEmits(['handleNodeClick', 'node-drop'])

const handleNodeClick = (node: any) => {
  node.open = !node.open
  emit('handleNodeClick', node.data)
}

type DropType = 'before' | 'after' | 'inner'
const buildNodeDropArgs = () => {
  const draggingNode = dragContext.dragNode as any
  const targetInfo = dragContext.targetInfo as any

  if (!draggingNode || !targetInfo) {
    return null
  }

  const newParent = targetInfo.parent ?? null
  const siblings = Array.isArray(targetInfo.siblings) ? targetInfo.siblings : []

  let newIndex =
    typeof targetInfo.indexBeforeDrop === 'number'
      ? targetInfo.indexBeforeDrop
      : siblings.indexOf(draggingNode)

  if (newIndex < 0) {
    newIndex = siblings.indexOf(draggingNode)
  }

  let dropNode: any | null = null
  let dropType: DropType = 'after'

  if (newParent && siblings.length === 1 && siblings[0] === draggingNode) {
    dropNode = newParent
    dropType = 'inner'
    return [draggingNode, dropNode, dropType] as const
  }

  if (siblings.length <= 1) {
    return [draggingNode, newParent, 'inner'] as const
  }

  if (newIndex === 0) {
    dropNode = siblings[1]
    dropType = 'before'
    return [draggingNode, dropNode, dropType] as const
  }

  dropNode = siblings[newIndex - 1]
  dropType = 'after'

  return [draggingNode, dropNode, dropType] as const
}
function onAfterDrop() {
  const args = buildNodeDropArgs()
  if (args) {
    emit('node-drop', args[0], args[1], args[2])
  }
}
const statHandler = (stat: any) => {
  stat.open = stat.level === 1
  return stat
}
</script>

<style lang="scss">
.maxkb-virtualized-tree {
  overflow: overlay !important;
  scrollbar-gutter: stable;

  ::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 5px;
    transition: all 0.2s ease-in-out;

    &:hover {
      cursor: pointer;
      background-color: rgba(0, 0, 0, 0.3);
    }
  }
  .tree-arrow-icon {
    color: var(--app-text-color-secondary);
    padding: 6px;
    font-size: 16px;
  }
  .tree-label {
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .tree-node {
    position: relative;
    border-radius: var(--el-border-radius-base);
    padding: 7px 0;
    cursor: pointer;
    width: 100%;
    box-sizing: border-box;
    &:hover {
      background: rgba(var(--el-text-color-primary-rgb), 0.1);
    }
    &:has(.maxkb-tree-node.is-current) {
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      font-weight: 500;
    }
  }
}
</style>
