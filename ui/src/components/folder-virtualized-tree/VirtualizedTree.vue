<template>
  <Draggable
    ref="treeRef"
    virtualization
    :defaultOpen="false"
    v-bind="$attrs"
    :model-value="filteredTreeData"
    class="maxkb-virtualized-tree"
    @click:node="handleNodeClick"
    @after-drop="onAfterDrop"
    :rootDroppable="false"
    :statHandler="statHandler"
    :disableDrag="!draggable"
    :disableDrop="!draggable"
  >
    <template #default="{ node, stat }">
      <div
        class="flex align-center maxkb-tree-node"
        :class="currentNodeKey === node.id ? 'is-current' : ''"
      >
        <el-icon
          @click.stop="stat.open = !stat.open"
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
import { ref, computed, nextTick } from 'vue'
import { Draggable, dragContext } from '@he-tree/vue'
import '@he-tree/vue/style/default.css'
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  currentNodeKey: {
    type: String,
    default: 'default',
  },
  filterNodeMethod: {
    type: Function,
    default: (node: any, filterText: string) => {
      return node.name?.toLowerCase().includes(filterText.toLowerCase())
    },
  },
  draggable: {
    type: Boolean,
    default: false,
  },
})

type DraggableInstance = InstanceType<typeof Draggable>
const treeRef = ref<DraggableInstance | null>(null)
const emit = defineEmits(['handleNodeClick', 'node-drop'])

const handleNodeClick = (node: any) => {
  if (node.data.id === props.currentNodeKey) {
    node.open = !node.open
    return
  }
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

const containsCurrentNodeKey = (node: any): boolean => {
  if (node.id === props.currentNodeKey) {
    return true
  }
  if (node.children && node.children.length) {
    return node.children.some((child: any) => containsCurrentNodeKey(child))
  }
  return false
}
const statHandler = (stat: any) => {
  stat.open = stat.level === 1
  if (filterText.value) {
    stat.open = true
  }
  if (containsCurrentNodeKey(stat.data)) {
    stat.open = true
  }
  return stat
}

// 过滤文本
const filterText = ref('')
/**
 * 递归过滤树
 * @param nodes 节点数组
 * @param text 过滤文本
 * @returns 过滤后的新树（新对象，但节点内的基本属性保持原引用）
 */
const filterTree = (nodes: any[], text: string): any[] => {
  if (!text || !props.filterNodeMethod) {
    return nodes
  }

  const result: any[] = []
  for (const node of nodes) {
    const isMatch = props.filterNodeMethod(node, text)
    let filteredChildren: any[] = []
    if (node.children && node.children.length) {
      filteredChildren = filterTree(node.children, text)
    }
    if (isMatch || filteredChildren.length) {
      // 创建新节点对象，保留原有属性，替换 children
      result.push({
        ...node,
        children: filteredChildren,
      })
    }
  }
  return result
}

// 计算过滤后的树数据
const filteredTreeData = computed(() => {
  return filterTree(props.modelValue, filterText.value)
})

// 暴露过滤方法给父组件
const filter = (text: string) => {
  filterText.value = text
}

defineExpose({
  filter,
})
</script>

<style lang="scss">
.maxkb-virtualized-tree {
  overflow: auto !important;
  scrollbar-gutter: stable;
  // 滚动条
  ::-webkit-scrollbar {
    width: 5px;
    height: 5px;
    -webkit-border-radius: 5px;
    -moz-border-radius: 5px;
    border-radius: 5px;
    background-color: transparent;
  }
  ::-webkit-scrollbar-thumb {
    transition: all 0.2s ease-in-out;
    background-color: transparent;
    background-clip: padding-box;
    -webkit-border-radius: 5px;
    -moz-border-radius: 5px;
    border-radius: 5px;
  }
  &:hover::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.1);
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
.he-tree-drag-placeholder {
  background-color: var(--el-color-primary-light-9);
  border: 2px dashed var(--el-color-primary);
  border-radius: 4px;
  width: 98%;
}
</style>
