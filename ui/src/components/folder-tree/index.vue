<template>
  <div class="folder-tree">
    <el-input
      v-model="filterText"
      :placeholder="$t('common.search')"
      prefix-icon="Search"
      clearable
      class="p-16 pb-0"
    />
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
        :data="data"
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
      :type="props.source"
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
import folderApi from '@/api/folder'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import useStore from '@/stores'
import { TreeToFlatten } from '@/utils/array'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import permissionMap from '@/permission'
import bus from '@/bus'
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

const allowDrag = (node: any) => {
  return permissionPrecise.value.folderEdit(node.data.id)
}

const allowDrop = (draggingNode: any, dropNode: any, type: string) => {
  const dropData = dropNode.data
  if (type === 'inner') {
    return permissionPrecise.value.folderEdit(dropData.id)
  }
  return false
}

const handleDrop = (draggingNode: any, dropNode: any, dropType: string, ev: DragEvent) => {
  const dragData = draggingNode.data
  const dropData = dropNode.data

  let newParentId: string
  if (dropType === 'inner') {
    newParentId = dropData.id
  } else {
    newParentId = dropData.parent_id
  }
  const obj = {
    ...dragData,
    parent_id: newParentId,
  }
  folderApi
    .putFolder(dragData.id, props.source, obj, loading)
    .then(() => {
      MsgSuccess(t('common.saveSuccess'))
      emit('refreshTree')
    })
    .catch(() => {
      emit('refreshTree')
    })
}

const { folder } = useStore()
onBeforeRouteLeave((to, from) => {
  folder.setCurrentFolder({})
})
onMounted(() => {
  bus.on('select_node', (id: string) => {
    treeRef.value?.setCurrentKey(id)
    hoverNodeId.value = id
  })
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
