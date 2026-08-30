<script setup lang="ts">
import { computed } from 'vue'
import { CaretBottom } from '@element-plus/icons-vue'
import { Draggable, dragContext } from '@he-tree/vue'
import '@he-tree/vue/style/default.css'
import type { FolderItem } from '@/api/types'
defineOptions({ name: 'FolderVirtualizedTree' })

interface FolderTreeNode extends Omit<FolderItem, 'children'> {
  children?: FolderTreeNode[]
  disabled?: boolean
}

interface FolderStat {
  children: FolderStat[]
  data: FolderTreeNode
  level: number
  open: boolean
}
type DropType = 'after' | 'before' | 'inner'

interface DropTargetInfo {
  indexBeforeDrop?: number
  parent?: FolderStat | null
  siblings?: FolderStat[]
}

const props = withDefaults(defineProps<{ canEdit?: boolean; currentNodeKey?: string; data?: FolderTreeNode[]; draggable?: boolean; filterText?: string }>(), {
  canEdit: true,
  currentNodeKey: '',
  data: () => [],
  draggable: false,
  filterText: '',
})

const emit = defineEmits<{
  create: [folder: FolderItem]
  delete: [folder: FolderItem]
  edit: [folder: FolderItem]
  move: [folder: FolderItem]
  nodeDrop: [draggingFolder: FolderItem, targetFolder: FolderItem, dropType: DropType]
  nodeClick: [folder: FolderItem]
}>()

// 过滤树
function filterFolders(folders: FolderTreeNode[], keyword: string): FolderTreeNode[] {
  if (!keyword) return folders

  return folders.reduce<FolderTreeNode[]>((filteredFolders, folder) => {
    const filteredChildren = filterFolders(folder.children ?? [], keyword)
    const folderMatched = folder.name.toLocaleLowerCase().includes(keyword)
    if (folderMatched || filteredChildren.length) {
      filteredFolders.push({ ...folder, children: filteredChildren })
    }
    return filteredFolders
  }, [])
}

const filteredTreeData = computed(() => filterFolders(props.data as FolderTreeNode[], props.filterText.trim().toLocaleLowerCase()))

// 点击展开或选择
function handleNodeClick(stat: FolderStat) {
  if (stat.data.disabled) return
  if (stat.data.id === props.currentNodeKey) {
    stat.open = !stat.open
    return
  }
  emit('nodeClick', stat.data)
}
function containsCurrentFolder(folder: FolderTreeNode): boolean {
  return folder.id === props.currentNodeKey || Boolean(folder.children?.some((child) => containsCurrentFolder(child)))
}

function handleStat<T extends FolderStat>(stat: T): T {
  if (props.filterText || containsCurrentFolder(stat.data)) stat.open = true
  return stat
}

// 拖拽
function buildNodeDropArgs() {
  const draggingNode = dragContext.dragNode as FolderStat | null
  const targetInfo = dragContext.targetInfo as DropTargetInfo | null
  if (!draggingNode || !targetInfo) return

  const parent = targetInfo.parent ?? null
  const siblings = targetInfo.siblings ?? []
  let newIndex = typeof targetInfo.indexBeforeDrop === 'number' ? targetInfo.indexBeforeDrop : siblings.indexOf(draggingNode)

  if (newIndex < 0) newIndex = siblings.indexOf(draggingNode)

  if (parent && siblings.length === 1 && siblings[0] === draggingNode) {
    return [draggingNode, parent, 'inner'] as const
  }
  if (siblings.length <= 1) {
    return parent ? ([draggingNode, parent, 'inner'] as const) : undefined
  }
  if (newIndex === 0) {
    const targetNode = siblings[1]
    return targetNode ? ([draggingNode, targetNode, 'before'] as const) : undefined
  }
  const targetNode = siblings[newIndex - 1]
  return targetNode ? ([draggingNode, targetNode, 'after'] as const) : undefined
}

function handleAfterDrop() {
  const dropArgs = buildNodeDropArgs()
  if (!dropArgs) return
  emit('nodeDrop', dropArgs[0].data, dropArgs[1].data, dropArgs[2])
}
</script>

<template>
  <Draggable
    class="mk-virtualized-tree h-full min-h-0"
    virtualization
    :default-open="false"
    v-bind="$attrs"
    :model-value="filteredTreeData"
    @click:node="handleNodeClick"
    @after-drop="handleAfterDrop"
    :statHandler="handleStat"
    :disableDrag="!draggable"
    :disableDrop="!draggable"
  >
    <template #default="{ node, stat }: { node: FolderTreeNode; stat: FolderStat }">
      <MkListItem :class="{ 'is-current': currentNodeKey === node.id, 'cursor-not-allowed! text-N400': node.disabled }" class="mk-tree-node">
        <template #default>
          <MkIcon
            @click.stop="stat.open = !stat.open"
            :icon="CaretBottom"
            :size="14"
            :style="{ visibility: stat.children.length ? 'visible' : 'hidden' }"
            class="text-N600! mr-1.5"
            :class="{ '-rotate-90': !stat.open }"
          />
          <slot name="default" v-bind="{ node, stat }">
            <span class="min-w-0 truncate" :title="node.name">{{ node.name }}</span>
          </slot>
        </template>

        <template #action-dropdown>
          <slot name="action-dropdown" :row="node"></slot>
        </template>
      </MkListItem>
    </template>
  </Draggable>
</template>

<style lang="scss">
.mk-virtualized-tree {
  --el-scrollbar-opacity: 0.3;
  --el-scrollbar-bg-color: var(--el-text-color-secondary);
  --el-scrollbar-hover-opacity: 0.5;
  --el-scrollbar-hover-bg-color: var(--el-text-color-secondary);
  scrollbar-color: transparent transparent;
  scrollbar-width: thin;

  &::-webkit-scrollbar {
    background-color: transparent;
    height: 6px;
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: transparent;
    border-radius: var(--el-border-radius-small);
    transition: background-color var(--el-transition-duration);
  }

  &:hover::-webkit-scrollbar-thumb {
    background-color: var(--el-scrollbar-bg-color);
    opacity: var(--el-scrollbar-opacity);
  }

  &:hover {
    scrollbar-color: color-mix(in srgb, var(--el-scrollbar-bg-color) 30%, transparent) transparent;
  }

  &::-webkit-scrollbar-thumb:hover {
    background-color: var(--el-scrollbar-bg-color);
    opacity: var(--el-scrollbar-hover-opacity);
  }

  .mk-tree-node {
    &:hover {
      background: none;
    }
  }
  .tree-node {
    border-radius: var(--el-border-radius-base);
    &:hover {
      background: var(--mk-N900-transparent-10);
    }
    &:has(.mk-tree-node.is-current) {
      background: rgb(var(--mk-primary-rgb) / 10%);
      color: var(--el-color-primary);
      font-weight: 500;
    }
  }
  .vtlist-inner {
    gap: calc(var(--spacing) * 1);
  }
}
</style>
