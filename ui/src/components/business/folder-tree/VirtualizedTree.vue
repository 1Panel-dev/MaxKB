<script setup lang="ts">
import { computed } from 'vue'
import { Draggable, dragContext } from '@he-tree/vue'
import '@he-tree/vue/style/default.css'
import type { WorkspaceFolder } from '@/api/types'

defineOptions({ name: 'FolderVirtualizedTree' })

interface FolderTreeNode extends Omit<WorkspaceFolder, 'children'> {
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

const props = withDefaults(
  defineProps<{
    canManage?: boolean
    currentNodeKey?: string
    data?: WorkspaceFolder[]
    draggable?: boolean
    filterText?: string
    protectedNodeId?: string
  }>(),
  {
    canManage: true,
    currentNodeKey: '',
    data: () => [],
    draggable: false,
    filterText: '',
    protectedNodeId: '',
  },
)

const emit = defineEmits<{
  create: [folder: WorkspaceFolder]
  delete: [folder: WorkspaceFolder]
  edit: [folder: WorkspaceFolder]
  move: [folder: WorkspaceFolder]
  nodeDrop: [draggingFolder: WorkspaceFolder, targetFolder: WorkspaceFolder, dropType: DropType]
  select: [folder: WorkspaceFolder]
}>()

const canDrag = computed(() => props.canManage && props.draggable && !props.filterText.trim())

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

const filteredTreeData = computed(() =>
  filterFolders(props.data as FolderTreeNode[], props.filterText.trim().toLocaleLowerCase()),
)

function containsCurrentFolder(folder: FolderTreeNode): boolean {
  return (
    folder.id === props.currentNodeKey ||
    Boolean(folder.children?.some((child) => containsCurrentFolder(child)))
  )
}

function handleStat<T extends FolderStat>(stat: T): T {
  stat.open = stat.level === 1
  if (props.filterText || containsCurrentFolder(stat.data)) stat.open = true
  return stat
}

function handleNodeClick(stat: FolderStat) {
  if (stat.data.disabled) return
  if (stat.data.id === props.currentNodeKey) {
    stat.open = !stat.open
    return
  }
  emit('select', stat.data)
}

function isNodeDraggable(stat: FolderStat) {
  return !stat.data.disabled && stat.data.id !== props.protectedNodeId
}

function isNodeDroppable(stat: FolderStat) {
  return !stat.data.disabled
}

function getNodeKey(stat: FolderStat) {
  return stat.data.id
}

function buildNodeDropArgs() {
  const draggingNode = dragContext.dragNode as FolderStat | null
  const targetInfo = dragContext.targetInfo as DropTargetInfo | null
  if (!draggingNode || !targetInfo) return

  const parent = targetInfo.parent ?? null
  const siblings = targetInfo.siblings ?? []
  let newIndex =
    typeof targetInfo.indexBeforeDrop === 'number'
      ? targetInfo.indexBeforeDrop
      : siblings.indexOf(draggingNode)

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
  <div class="h-full min-h-0">
    <Draggable
      v-if="filteredTreeData.length"
      aria-label="文件夹树"
      class="folder-virtualized-tree"
      :default-open="false"
      :disable-drag="!canDrag"
      :disable-drop="!canDrag"
      :each-draggable="isNodeDraggable"
      :each-droppable="isNodeDroppable"
      :model-value="filteredTreeData"
      :node-key="getNodeKey"
      :root-droppable="false"
      :stat-handler="handleStat"
      virtualization
      @after-drop="handleAfterDrop"
      @click:node="handleNodeClick"
    >
      <template #default="{ node, stat }: { node: FolderTreeNode; stat: FolderStat }">
        <div
          class="folder-tree-node group flex min-w-0 items-center"
          :class="{
            'is-current': currentNodeKey === node.id,
            'is-disabled': node.disabled,
          }"
        >
          <button
            type="button"
            class="folder-tree-arrow flex-center shrink-0"
            :class="{ 'rotate-90': stat.open }"
            :style="{ visibility: stat.children.length ? 'visible' : 'hidden' }"
            aria-label="展开或收起文件夹"
            @click.stop="stat.open = !stat.open"
          >
            <MkIcon name="icon_right_outlined" :size="16" />
          </button>

          <div class="flex min-w-0 flex-1 items-center gap-2 pr-2">
            <MkIcon name="icon_file-folder_colorful" :size="18" />
            <span class="min-w-0 flex-1 truncate" :title="node.name">{{ node.name }}</span>

            <MkDropdown v-if="canManage" trigger="click" :teleported="false">
              <el-button text class="group-hover-visible -mr-1" @click.stop>
                <MkIcon name="icon_more_outlined" />
              </el-button>
              <template #dropdown>
                <MkDropdownMenu>
                  <MkDropdownItem @click="emit('create', node)">
                    <template #icon><MkIcon name="icon_add_outlined" /></template>
                    <span>创建子文件夹</span>
                  </MkDropdownItem>
                  <MkDropdownItem @click="emit('edit', node)">
                    <template #icon><MkIcon name="icon_edit_outlined" /></template>
                    <span>编辑</span>
                  </MkDropdownItem>
                  <MkDropdownItem
                    :disabled="node.id === protectedNodeId"
                    @click="emit('move', node)"
                  >
                    <template #icon><MkIcon name="icon_right_outlined" /></template>
                    <span>移动到</span>
                  </MkDropdownItem>
                  <MkDropdownItem
                    divided
                    :disabled="node.id === protectedNodeId"
                    @click="emit('delete', node)"
                  >
                    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                    <span>删除</span>
                  </MkDropdownItem>
                </MkDropdownMenu>
              </template>
            </MkDropdown>
          </div>
        </div>
      </template>
    </Draggable>

    <p v-else class="pt-20 text-center text-N600">暂无文件夹</p>
  </div>
</template>

<style lang="scss" scoped>
.folder-virtualized-tree {
  height: 100%;
  overflow: auto;
  scrollbar-gutter: stable;

  :deep(.he-tree-drag-placeholder) {
    background-color: color-mix(in srgb, var(--mk-primary) 10%, transparent);
    border: 2px dashed var(--mk-primary);
    border-radius: var(--el-border-radius-base);
    width: 98%;
  }

  :deep(.tree-node) {
    border-radius: var(--el-border-radius-base);
    cursor: pointer;
    padding: 2px 0;
  }
}

.folder-tree-arrow {
  background: transparent;
  border: 0;
  color: var(--mk-N600);
  height: calc(var(--spacing) * 9);
  padding: 0;
  transition: transform 0.2s;
  width: calc(var(--spacing) * 7);
}

.folder-tree-node {
  border-radius: var(--el-border-radius-base);
  min-height: calc(var(--spacing) * 9);
  width: 100%;

  &:hover {
    background-color: color-mix(in srgb, var(--mk-N900) 6%, transparent);
  }

  &.is-current {
    background-color: color-mix(in srgb, var(--mk-primary) 10%, transparent);
    color: var(--mk-primary);
    font-weight: 500;
  }

  &.is-disabled {
    color: var(--mk-N600);
    cursor: not-allowed;
    opacity: 0.6;
  }
}
</style>
