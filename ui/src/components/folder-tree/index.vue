<template>
  <div class="folder-tree">
    <div class="flex ml-4 p-8 pb-0">
      <el-input
        v-model="filterText"
        :placeholder="$t('common.search')"
        prefix-icon="Search"
        clearable
      />
      <el-dropdown trigger="click" :teleported="false" @command="switchSortMethod">
        <el-button class="ml-4">
          <AppIcon :iconName="sortIconName"></AppIcon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu class="w-180">
            <template v-for="(group, index) in SORT_MENU_CONFIG" :key="index">
              <el-dropdown-item
                v-for="obj in group.items"
                :key="obj.value"
                :command="obj.value"
                :class="`${currentSort === obj.value ? 'active' : ''} flex-between`"
              >
                <span>
                  {{ obj.label }}
                </span>

                <el-icon v-if="currentSort === obj.value" class="ml-4">
                  <Check />
                </el-icon>
              </el-dropdown-item>
              <el-divider class="mb-4 mt-4" v-if="index < SORT_MENU_CONFIG.length - 1"></el-divider>
            </template>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <div class="p-8 pb-0" v-if="showShared && hasPermission(EditionConst.IS_EE, 'OR')">
      <div class="border-b">
        <div
          @click="handleSharedNodeClick"
          class="shared-button flex cursor border-r-6"
          :class="currentNodeKey === 'share' && 'active'"
        >
          <AppIcon
            iconName="app-shared-active"
            style="font-size: 18px"
            class="color-primary"
          ></AppIcon>
          <span class="ml-8">{{ shareTitle }}</span>
        </div>
      </div>
    </div>

    <el-scrollbar>
      <el-tree
        class="folder-tree__main p-8"
        :class="
          showShared && hasPermission(EditionConst.IS_EE, 'OR')
            ? 'tree-height-shared'
            : 'tree-height '
        "
        :style="treeStyle"
        ref="treeRef"
        :data="sortedData"
        :props="defaultProps"
        @node-click="handleNodeClick"
        :filter-node-method="filterNode"
        :default-expanded-keys="[currentNodeKey]"
        :current-node-key="currentNodeKey"
        highlight-current
        :draggable="draggable"
        :allow-drop="allowDrop"
        :allow-drag="allowDrag"
        @node-drop="handleDrop"
        node-key="id"
        v-loading="loading"
        v-bind="$attrs"
      >
        <template #default="{ node, data }">
          <div
            @mouseenter.stop="handleMouseEnter(data)"
            class="flex align-center w-full custom-tree-node"
          >
            <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
            <span class="tree-label ml-8" :title="node.label">{{ i18n_name(node.label) }}</span>

            <div
              v-if="canOperation && MoreFilledPermission(node, data)"
              @click.stop
              v-show="hoverNodeId === data.id"
              @mouseenter.stop="handleMouseEnter(data)"
              @mouseleave.stop="handleMouseleave"
              class="mr-8 tree-operation-button"
            >
              <el-dropdown trigger="click" :teleported="false">
                <el-button text class="w-full" v-if="MoreFilledPermission(node, data)">
                  <AppIcon iconName="app-more"></AppIcon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      @click.stop="openCreateFolder(data)"
                      v-if="permissionPrecise.folderCreate(data.id)"
                    >
                      <AppIcon iconName="app-add-folder" class="color-secondary"></AppIcon>
                      {{ $t('components.folder.addChildFolder') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      @click.stop="openEditFolder(data)"
                      v-if="permissionPrecise.folderEdit(data.id)"
                    >
                      <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                      {{ $t('common.edit') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      @click.stop="openMoveToDialog(data)"
                      v-if="node.level !== 1 && permissionPrecise.folderEdit(data.id)"
                    >
                      <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                      {{ $t('common.moveTo') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      @click.stop="openAuthorization(data)"
                      v-if="permissionPrecise.folderAuth(data.id)"
                    >
                      <AppIcon
                        iconName="app-resource-authorization"
                        class="color-secondary"
                      ></AppIcon>
                      {{ $t('views.system.resourceAuthorization.title') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      divided
                      @click.stop="deleteFolder(data)"
                      :disabled="!data.parent_id"
                      v-if="permissionPrecise.folderDelete(data.id)"
                    >
                      <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                      {{ $t('common.delete') }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
      </el-tree>
    </el-scrollbar>

    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" :title="title" />
    <MoveToDialog ref="MoveToDialogRef" :source="props.source" @refresh="emit('refreshTree')" />
    <ResourceAuthorizationDrawer
      :type="`${props.source}_FOLDER`"
      :is-folder="true"
      :is-root-folder="!currentNode?.parent_id"
      ref="ResourceAuthorizationDrawerRef"
    />
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import type { TreeInstance } from 'element-plus'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import { t } from '@/locales'
import MoveToDialog from '@/components/folder-tree/MoveToDialog.vue'
import { i18n_name } from '@/utils/common'
import { SORT_MENU_CONFIG, SORT_TYPES, type SortType } from '@/components/folder-tree/constant'
import { debounce } from 'lodash-es'
import { encode, mid, rebalance } from '@/utils/folder'
import folderApi from '@/api/workspace/folder'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import useStore from '@/stores'
import { TreeToFlatten } from '@/utils/array'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import permissionMap from '@/permission'
import bus from '@/bus'
const { folder, user } = useStore()

defineOptions({ name: 'FolderTree' })
const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  currentNodeKey: {
    type: String,
    default: 'default',
  },
  source: {
    type: String,
    default: 'APPLICATION',
  },
  showShared: {
    type: Boolean,
    default: false,
  },
  shareTitle: {
    type: String,
    default: '',
  },
  canOperation: {
    type: Boolean,
    default: true,
  },
  treeStyle: {
    type: Object,
    default: () => ({}),
  },
  draggable: {
    type: Boolean,
    default: false,
  },
})
const resourceType = computed(() => {
  if (props.source === 'APPLICATION') {
    return 'application'
  } else if (props.source === 'KNOWLEDGE') {
    return 'knowledge'
  } else if (props.source === 'MODEL') {
    return 'model'
  } else if (props.source === 'TOOL') {
    return 'tool'
  } else {
    return 'application'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap[resourceType.value!]['workspace']
})

const MoreFilledPermission = (node: any, data: any) => {
  return (
    permissionPrecise.value.folderCreate(data.id) ||
    permissionPrecise.value.folderEdit(data.id) ||
    permissionPrecise.value.folderDelete(data.id) ||
    permissionPrecise.value.folderAuth(data.id)
  )
}

const MoveToDialogRef = ref()
function openMoveToDialog(data: any) {
  const obj = {
    id: data.id,
    folder_type: props.source,
  }
  MoveToDialogRef.value.open(obj, true)
}

const CUSTOM_STORAGE_KEY = `${user.userInfo?.id}-${props.source}-folder-custom-positions`
const FOLDER_SORT_TYPE = `${user.userInfo?.id}-${props.source}-folder-sort-type`

const dataWithOrder = computed(() => {
  if (currentSort.value !== SORT_TYPES.CUSTOM || !props.data?.length) {
    return props.data
  }

  const rootNode: any = props.data[0]

  return [
    {
      ...rootNode,
      children: rootNode.children ? addOrderToTree(rootNode.children, rootNode.id) : [],
    },
  ]
})

function addOrderToTree(nodes: any, parentId: string): Node[] {
  if (!nodes || nodes.length === 0) {
    return nodes
  }

  const positions = getPositions(parentId)
  let needSave = false

  nodes.forEach((node: any) => {
    if (positions[node.id] === undefined) {
      const existingPositions: any = Object.values(positions)
      const maxPos = existingPositions.length > 0 ? Math.max(...existingPositions) : 0

      positions[node.id] = maxPos + encode(1, 0)
      needSave = true
    }
  })

  if (needSave) {
    savePositionsInit(parentId, positions)
  }
  return nodes.map((node: any) => ({
    ...node,
    order: positions[node.id] ?? Infinity,
    children:
      node.children && node.children.length > 0
        ? addOrderToTree(node.children, node.id)
        : node.children,
  }))
}

const sortIconName = computed(() => {
  const sort = currentSort.value
  if (sort.endsWith('asc')) {
    return 'app-folder-asc'
  }
  if (sort.endsWith('desc')) {
    return 'app-folder-desc'
  }
  return 'app-folder-custom'
})

const currentSort = ref<SortType>(SORT_TYPES.CREATE_TIME_DESC)
const sortedData = computed(() => {
  const treeData = dataWithOrder.value

  const sortMethods = {
    [SORT_TYPES.CREATE_TIME_ASC]: (a: any, b: any) =>
      new Date(a.create_time).getTime() - new Date(b.create_time).getTime(),
    [SORT_TYPES.CREATE_TIME_DESC]: (a: any, b: any) =>
      new Date(b.create_time).getTime() - new Date(a.create_time).getTime(),
    [SORT_TYPES.NAME_ASC]: (a: any, b: any) => a.name.localeCompare(b.name),
    [SORT_TYPES.NAME_DESC]: (a: any, b: any) => b.name.localeCompare(a.name),
    [SORT_TYPES.CUSTOM]: (a: any, b: any) => a.order - b.order,
  }

  const compareFn = sortMethods[currentSort.value]
  if (!treeData || !compareFn) {
    return treeData
  }

  return sortTreeData(treeData, compareFn)
})

// 获取指定父节点的位置数据
function getPositions(parentId: string) {
  try {
    const data = localStorage.getItem(CUSTOM_STORAGE_KEY)
    const allNodesData = data ? JSON.parse(data) : {}
    return allNodesData[parentId] || {}
  } catch (error) {
    MsgError(error as string)
    return {}
  }
}

function doSave(parentId: string, positions: Record<string, number>) {
  try {
    const data = localStorage.getItem(CUSTOM_STORAGE_KEY)
    const allNodesData = data ? JSON.parse(data) : {}
    allNodesData[parentId] = positions
    localStorage.setItem(CUSTOM_STORAGE_KEY, JSON.stringify(allNodesData))
  } catch (error) {
    MsgError(error as string)
  }
}

const savePositions = debounce(doSave, 300)

function savePositionsInit(parentId: string, positions: Record<string, number>) {
  doSave(parentId, positions)
}

function collectAllPositions(parentId: string, children: any[]) {
  const allPositions: Record<string, Record<string, number>> = {}
  if (!children || children.length === 0) {
    return allPositions
  }

  const positions: Record<string, number> = {}
  children.forEach((child, index) => {
    positions[child.id] = encode(index + 1, 0)

    if (child.children && child.children.length > 0) {
      const childPositions = collectAllPositions(child.id, child.children)
      Object.assign(allPositions, childPositions)
    }
  })
  allPositions[parentId] = positions
  return allPositions
}

function initAllPositions(parentId: string, children: any[]) {
  const allPositions = collectAllPositions(parentId, children)
  localStorage.setItem(CUSTOM_STORAGE_KEY, JSON.stringify(allPositions))
}

// 对原始数据递归排序
function sortTreeData(nodes: any[], compareFn: (a: any, b: any) => number): any[] {
  if (!compareFn || nodes.length === 0 || !nodes) {
    return nodes
  }
  const sortedNodes = [...nodes].sort(compareFn)
  return sortedNodes.map((node) => ({
    ...node,
    children:
      node.children && node.children.length > 0
        ? sortTreeData(node.children, compareFn)
        : node.children,
  }))
}

function switchSortMethod(method: SortType) {
  currentSort.value = method
  localStorage.setItem(FOLDER_SORT_TYPE, method)

  if (method === SORT_TYPES.CUSTOM) {
    const rootNode: any = props.data?.[0]
    if (rootNode) {
      const folderPositions = getPositions(rootNode.id)
      if (Object.keys(folderPositions).length === 0) {
        if (rootNode.children?.length > 0) {
          initAllPositions(rootNode.id, rootNode.children)
        }
      }
    }
  }
}

const allowDrag = (node: any) => {
  return permissionPrecise.value.folderEdit(node.data.id)
}

const allowDrop = (draggingNode: any, dropNode: any, type: string) => {
  const dropData = dropNode.data
  if (type === 'inner') {
    return permissionPrecise.value.folderEdit(dropData.id)
  } else if ((type === 'prev' || type === 'next') && currentSort.value === SORT_TYPES.CUSTOM) {
    if (!dropData.parent_id) {
      return false
    } else {
      return permissionPrecise.value.folderEdit(dropData.parent_id)
    }
  }
  return false
}

const handleDrop = (draggingNode: any, dropNode: any, dropType: string, ev: DragEvent) => {
  const dragData = draggingNode.data
  const dropData = dropNode.data

  const oldParentId = dragData.parent_id
  let newParentId: string
  if (dropType === 'inner') {
    newParentId = dropData.id
  } else if (dropType === 'prev' || dropType === 'next') {
    newParentId = dropData.parent_id
  } else {
    newParentId = dropData.parent_id
  }

  const isCrossNode: boolean = oldParentId !== newParentId

  if (isCrossNode) {
    const obj = {
      ...dragData,
      parent_id: newParentId,
    }
    folderApi
      .putFolder(dragData.id, props.source, obj, loading)
      .then(() => {
        sortAfterDrop(dragData, dropData, dropType, newParentId)

        MsgSuccess(t('common.saveSuccess'))
      })
      .catch(() => {
        emit('refreshTree')
      })
  } else {
    // 同级拖拽，直接放置
    sortAfterDrop(dragData, dropData, dropType, newParentId)
  }
}

function sortAfterDrop(
  draggingNodeData: any,
  dropNodeData: any,
  dropType: string,
  newParentId: string,
) {
  const sortMethod = localStorage.getItem(FOLDER_SORT_TYPE)
  currentSort.value = sortMethod as SortType

  if (sortMethod === SORT_TYPES.CUSTOM) {
    const positions = getPositions(newParentId)
    let prevPos: number
    let nextPos: number
    if (dropType === 'inner') {
      const childrenPositions: number[] = Object.values(positions)
      if (childrenPositions.length === 0) {
        positions[draggingNodeData.id] = encode(1, 0)
        savePositions(newParentId, positions)
        return
      }
      // 放到最后
      const maxPos = Math.max(...childrenPositions)
      positions[draggingNodeData.id] = maxPos + encode(1, 0)
      savePositions(newParentId, positions)
    } else if (dropType === 'before') {
      const { dropPos, sortedNodes, dropIndex } = getSortContext(positions, dropNodeData.id)
      const prevNode: any[] = sortedNodes[dropIndex - 1]

      prevPos = prevNode ? prevNode[1] : 0
      nextPos = dropPos

      const newPos = mid(prevPos, nextPos)

      if (newPos === null) {
        // rebalance
        rebalanceAndInsert(newParentId, draggingNodeData.id, dropNodeData.id, 'before')
        return
      }
      positions[draggingNodeData.id] = newPos
      savePositions(newParentId, positions)
    } else if (dropType === 'after') {
      const { dropPos, sortedNodes, dropIndex } = getSortContext(positions, dropNodeData.id)
      const nextNode: any[] = sortedNodes[dropIndex + 1]

      prevPos = dropPos
      nextPos = nextNode ? nextNode[1] : Infinity

      if (nextPos === Infinity) {
        positions[draggingNodeData.id] = prevPos + encode(1, 0)
      } else {
        const newPos = mid(prevPos, nextPos)

        if (newPos === null) {
          rebalanceAndInsert(newParentId, draggingNodeData.id, dropNodeData.id, 'after')
          return
        }
        positions[draggingNodeData.id] = newPos
      }

      savePositions(newParentId, positions)
    }
  } else {
    emit('refreshTree')
  }
}

function getSortContext(positions: Record<string, number>, nodeId: string) {
  const dropPos = positions[nodeId]
  const sortedNodes = Object.entries(positions).sort((a: any[], b: any[]) => a[1] - b[1])
  const dropIndex = sortedNodes.findIndex(([id]) => id === nodeId)

  return { dropPos, sortedNodes, dropIndex }
}

function rebalanceAndInsert(
  parentId: string,
  dragNodeId: string,
  dropNodeId: string,
  position: 'before' | 'after',
) {
  const positions = getPositions(parentId)
  const sortedIds = Object.entries(positions)
    .sort((a: any[], b: any[]) => a[1] - b[1])
    .map(([id]) => id)

  const dragIndex = sortedIds.indexOf(dragNodeId)
  if (dragIndex > -1) {
    sortedIds.splice(dragIndex, 1)
  }
  const dropIndex = sortedIds.indexOf(dropNodeId)
  if (position === 'before') {
    sortedIds.splice(dropIndex, 0, dragNodeId)
  } else {
    sortedIds.splice(dropIndex + 1, 0, dragNodeId)
  }

  const tempPositions: Record<string, number> = {}
  sortedIds.forEach((id, index) => {
    tempPositions[id] = index
  })

  const newPositions = rebalance(tempPositions)
  savePositionsInit(parentId, newPositions)
  // rebalance finish
}

onBeforeRouteLeave((to, from) => {
  folder.setCurrentFolder({})
})

function loadSortPreference() {
  const savedSort = localStorage.getItem(FOLDER_SORT_TYPE)
  if (savedSort) {
    currentSort.value = savedSort as SortType
  }
}

onMounted(() => {
  bus.on('select_node', (id: string) => {
    treeRef.value?.setCurrentKey(id)
    hoverNodeId.value = id
  })
  loadSortPreference()
})
interface Tree {
  name: string
  children?: Tree[]
  id?: string
  show?: boolean
  parent_id?: string
}

const defaultProps = {
  children: 'children',
  label: 'name',
}

const emit = defineEmits(['handleNodeClick', 'refreshTree'])

const treeRef = ref<TreeInstance>()
const filterText = ref('')
const hoverNodeId = ref<string | undefined>('')
const title = ref('')
const loading = ref(false)

watch(filterText, (val) => {
  treeRef.value!.filter(val)
})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

let time: any

function handleMouseEnter(data: Tree) {
  clearTimeout(time)
  hoverNodeId.value = data.id
}
function handleMouseleave() {
  time = setTimeout(() => {
    clearTimeout(time)
    document.body.click()
  }, 300)
}

const handleNodeClick = (data: Tree) => {
  emit('handleNodeClick', data)
}

const handleSharedNodeClick = () => {
  treeRef.value?.setCurrentKey(undefined)
  emit('handleNodeClick', { id: 'share', name: props.shareTitle })
}

function deleteFolder(row: Tree) {
  MsgConfirm(
    `${t('common.deleteConfirm')}：${row.name}`,
    t('components.folder.deleteConfirmMessage'),
    {
      confirmButtonText: t('common.delete'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      folderApi.delFolder(row.id as string, props.source, loading).then(() => {
        treeRef.value?.setCurrentKey(row.parent_id || 'default')
        const prevFolder = TreeToFlatten(props.data).find((item: any) => item.id === row.parent_id)
        folder.setCurrentFolder(prevFolder)

        if (currentSort.value === SORT_TYPES.CUSTOM) {
          const parentId = row.parent_id || 'default'
          const positions = getPositions(parentId)

          if (positions[row.id as string] !== undefined) {
            delete positions[row.id as string]
            savePositionsInit(parentId, positions)
          }
        }
        emit('refreshTree')
      })
    })
    .catch(() => {})
}

const CreateFolderDialogRef = ref()
function openCreateFolder(row: Tree) {
  title.value = t('components.folder.addChildFolder')
  CreateFolderDialogRef.value.open(props.source, row.id)
}
function openEditFolder(row: Tree) {
  title.value = t('components.folder.editFolder')
  CreateFolderDialogRef.value.open(props.source, row.id, row)
}

const currentNode = ref<Tree | null>(null)
const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(data: any) {
  currentNode.value = data
  ResourceAuthorizationDrawerRef.value.open(data.id, data)
}

function refreshFolder() {
  emit('refreshTree')
}

function clearCurrentKey() {
  treeRef.value?.setCurrentKey(undefined)
}
defineExpose({
  clearCurrentKey,
})
onUnmounted(() => {
  treeRef.value?.setCurrentKey(undefined)
})
</script>
<style lang="scss" scoped>
.folder-tree {
  .shared-button {
    padding: 10px 8px;
    font-weight: 400;
    font-size: 14px;
    margin-bottom: 4px;
    &.active {
      background: var(--el-color-primary-light-9);
      border-radius: var(--app-border-radius-small);
      color: var(--el-color-primary);
      font-weight: 500;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
    }
    &:hover {
      border-radius: var(--app-border-radius-small);
      background: var(--app-text-color-light-1);
    }
    &.is-active {
      &:hover {
        color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
    }
  }
  .tree-height-shared {
    padding-top: 4px;
    height: calc(100vh - 220px);
  }
  .tree-height {
    padding-top: 4px;
    height: calc(100vh - 180px);
  }
  :deep(.folder-tree__main) {
    .el-tree-node.is-dragging {
      opacity: 0.5;
    }
    .el-tree-node.is-drop-inner > .el-tree-node__content {
      background-color: var(--el-color-primary-light-9);
      border: 2px dashed var(--el-color-primary);
      border-radius: 4px;
    }
    .custom-tree-node {
      box-sizing: content-box;
      width: calc(100% - 27px);
    }
    .tree-label {
      width: 100%;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .el-tree-node__content {
      position: relative;
    }
    .el-tree-node__children {
      overflow: inherit !important;
    }
  }
}
</style>
