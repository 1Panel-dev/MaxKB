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
        <el-button class="ml-8" style="width: 32px">
          <AppIcon :iconName="sortIconName"></AppIcon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu style="width: 220px">
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
    <VirtualizedTree
      ref="treeRef"
      class="folder-tree__main"
      v-model="sortedData"
      :class="
        showShared && hasPermission(EditionConst.IS_EE, 'OR') ? 'tree-height-shared' : 'tree-height'
      "
      @node-drop="handleDrop"
      @handleNodeClick="handleNodeClick"
      :current-node-key="currentNodeKey"
      :filter-node-method="filterNode"
      :draggable="draggable"
      :style="treeStyle"
    >
      <template #default="{ node, stat }">
        <div @mouseenter.stop="handleMouseEnter(node)" class="flex align-center custom-tree-node">
          <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
          <span class="tree-label ml-8 lighter" :title="node.name">{{ i18n_name(node.name) }}</span>
          <div
            v-if="canOperation && MoreFilledPermission(node) && hoverNodeId === node.id"
            @click.stop
            @mouseenter.stop="handleMouseEnter(node)"
            @mouseleave.stop="handleMouseleave"
            class="mr-8 tree-operation-button"
          >
            <el-dropdown trigger="click" @visible-change="onDropdownVisibleChange">
              <el-button text class="w-full" v-if="MoreFilledPermission(node)">
                <AppIcon iconName="app-more"></AppIcon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    @click.stop="openCreateFolder(node)"
                    v-if="permissionPrecise.folderCreate(node.id)"
                  >
                    <AppIcon iconName="app-add-folder" class="color-secondary"></AppIcon>
                    {{ $t('components.folder.addChildFolder') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="openEditFolder(node)"
                    v-if="permissionPrecise.folderEdit(node.id)"
                  >
                    <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                    {{ $t('common.edit') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="openMoveToDialog(node)"
                    v-if="node.level !== 1 && permissionPrecise.folderEdit(node.id)"
                  >
                    <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                    {{ $t('common.moveTo') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="openAuthorization(node)"
                    v-if="permissionPrecise.folderAuth(node.id)"
                  >
                    <AppIcon
                      iconName="app-resource-authorization"
                      class="color-secondary"
                    ></AppIcon>
                    {{ $t('views.system.resourceAuthorization.title') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    divided
                    @click.stop="deleteFolder(node)"
                    :disabled="!node.parent_id"
                    v-if="permissionPrecise.folderDelete(node.id)"
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
    </VirtualizedTree>

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
import VirtualizedTree from './VirtualizedTree.vue'
import CreateFolderDialog from '@/components/folder-virtualized-tree/CreateFolderDialog.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import MoveToDialog from '@/components/folder-virtualized-tree/MoveToDialog.vue'
import {
  SORT_MENU_CONFIG,
  SORT_TYPES,
  type SortType,
} from '@/components/folder-virtualized-tree/constant'
import { t } from '@/locales'
import { debounce } from 'lodash'
import { i18n_name } from '@/utils/common'
import { encode, mid, rebalance } from '@/utils/folder'
import folderApi from '@/api/workspace/folder'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { TreeToFlatten } from '@/utils/array'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import permissionMap from '@/permission'
import useStore from '@/stores'
import bus from '@/bus'

const { folder, user } = useStore()

defineOptions({ name: 'FolderVirtualizedTree' })
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

onBeforeRouteLeave((to, from) => {
  if (from?.name === 'ToolWorkflow') return
  if (from?.name === 'AppSetting') return
  folder.setCurrentFolder({})
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

const MoreFilledPermission = (node: any) => {
  return (
    permissionPrecise.value.folderCreate(node.id) ||
    permissionPrecise.value.folderEdit(node.id) ||
    permissionPrecise.value.folderDelete(node.id) ||
    permissionPrecise.value.folderAuth(node.id)
  )
}

const emit = defineEmits(['handleNodeClick', 'refreshTree'])

const treeRef = ref()
const filterText = ref('')
const hoverNodeId = ref<string | undefined>('')
const title = ref('')
const loading = ref(false)

watch(filterText, (val) => {
  let v = val
  if (val) {
    v = val.trim()
  }
  treeRef.value!.filter(v)
})
const filterNode = (data: any, value: string) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

const handleDrop = (draggingNode: any, dropNode: any, dropType: string) => {
  const dragData = draggingNode.data
  const dropData = dropNode.data
  console.log(draggingNode, dropNode, dropType)

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
        emit('refreshTree')

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

const savePositions = debounce(doSave, 300)
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
function getSortContext(positions: Record<string, number>, nodeId: string) {
  const dropPos = positions[nodeId]
  const sortedNodes = Object.entries(positions).sort((a: any[], b: any[]) => a[1] - b[1])
  const dropIndex = sortedNodes.findIndex(([id]) => id === nodeId)

  return { dropPos, sortedNodes, dropIndex }
}

const isDropdownOpen = ref(false)
let time: any

function handleMouseEnter(data: any) {
  clearTimeout(time)
  hoverNodeId.value = data.id
}
function handleMouseleave() {
  if (isDropdownOpen.value) return
  time = setTimeout(() => {
    clearTimeout(time)
    document.body.click()
  }, 300)
}
const onDropdownVisibleChange = (visible: boolean) => {
  isDropdownOpen.value = visible
}

const handleSharedNodeClick = () => {
  emit('handleNodeClick', { id: 'share', name: props.shareTitle })
}

const handleNodeClick = (node: any) => {
  emit('handleNodeClick', node)
}

// 删除文件夹
function deleteFolder(row: any) {
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
// 创建文件夹
const CreateFolderDialogRef = ref()
function openCreateFolder(row: any) {
  title.value = t('components.folder.addChildFolder')
  CreateFolderDialogRef.value.open(props.source, row.id)
}
function openEditFolder(row: any) {
  title.value = t('components.folder.editFolder')
  CreateFolderDialogRef.value.open(props.source, row.id, row)
}

// 授权
const currentNode = ref<any>(null)
const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(data: any) {
  currentNode.value = data
  ResourceAuthorizationDrawerRef.value.open(data.id, data)
}
// 移动到
const MoveToDialogRef = ref()
function openMoveToDialog(data: any) {
  const obj = {
    id: data.id,
    folder_type: props.source,
  }
  MoveToDialogRef.value.open(obj, true)
}

// 排序

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

const CUSTOM_STORAGE_KEY = `${user.userInfo?.id}-${user.getWorkspaceId()}-${props.source}-folder-custom-positions`
const FOLDER_SORT_TYPE = `${user.userInfo?.id}-${user.getWorkspaceId()}-${props.source}-folder-sort-type`

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

function initAllPositions(parentId: string, children: any[]) {
  const allPositions = collectAllPositions(parentId, children)
  localStorage.setItem(CUSTOM_STORAGE_KEY, JSON.stringify(allPositions))
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

function savePositionsInit(parentId: string, positions: Record<string, number>) {
  doSave(parentId, positions)
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

function refreshFolder() {
  emit('refreshTree')
}

function loadSortPreference() {
  const savedSort = localStorage.getItem(FOLDER_SORT_TYPE)
  if (savedSort) {
    currentSort.value = savedSort as SortType
  }
}

defineExpose({})

onMounted(() => {
  bus.on('select_node', (id: string) => {
    hoverNodeId.value = id
  })
  loadSortPreference()
})

onUnmounted(() => {})
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
      background: rgba(var(--el-text-color-primary-rgb), 0.1);
    }
    &.is-active {
      &:hover {
        color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
    }
  }
  .tree-height-shared {
    height: calc(100vh - 220px);
  }
  .tree-height {
    height: calc(100vh - 180px);
  }
  :deep(.folder-tree__main) {
    padding: 4px 2px 0 8px;
    .custom-tree-node {
      box-sizing: content-box;
      position: relative;
    }
  }
}
</style>
