<template>
  <div class="folder-tree">
    <el-input
      v-model="filterText"
      :placeholder="$t('common.search')"
      prefix-icon="Search"
      clearable
      class="p-8"
    />
    <div class="tree-height" :style="treeStyle">
      <div v-if="showShared && hasPermission(EditionConst.IS_EE, 'OR')" class="border-b mb-4">
        <div
          @click="handleSharedNodeClick"
          class="shared-button flex cursor"
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

      <el-scrollbar>
        <el-tree
          ref="treeRef"
          :data="data"
          :props="defaultProps"
          @node-click="handleNodeClick"
          :filter-node-method="filterNode"
          :default-expanded-keys="[currentNodeKey]"
          :current-node-key="currentNodeKey"
          highlight-current
          class="overflow-inherit_node__children"
          node-key="id"
          v-loading="loading"
          v-bind="$attrs"
        >
          <template #default="{ node, data }">
            <div class="flex-between w-full" @mouseenter.stop="handleMouseEnter(data)">
              <div class="flex align-center">
                <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
                <span class="ml-8 ellipsis" style="max-width: 110px" :title="node.label">{{
                  node.label
                }}</span>
              </div>

              <div
                v-if="canOperation"
                @click.stop
                v-show="hoverNodeId === data.id"
                @mouseenter.stop="handleMouseEnter(data)"
                @mouseleave.stop="handleMouseleave"
                class="mr-16"
              >
                <el-dropdown trigger="click" :teleported="false">
                  <el-button text class="w-full" v-if="MoreFilledPermission(node)">
                    <AppIcon iconName="app-more"></AppIcon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        @click.stop="openCreateFolder(data)"
                        v-if="node.level !== 3 && permissionPrecise.folderCreate()"
                      >
                        <AppIcon iconName="app-add-folder" class="color-secondary"></AppIcon>
                        {{ $t('components.folder.addChildFolder') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        @click.stop="openEditFolder(data)"
                        v-if="permissionPrecise.folderEdit()"
                      >
                        <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                        {{ $t('common.edit') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        divided
                        @click.stop="deleteFolder(data)"
                        :disabled="!data.parent_id"
                        v-if="permissionPrecise.folderDelete()"
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
    </div>
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" :title="title" />
  </div>
</template>

<script lang="ts" setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import type { TreeInstance } from 'element-plus'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import { t } from '@/locales'
import folderApi from '@/api/folder'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import useStore from '@/stores'
import { TreeToFlatten } from '@/utils/array'
import { MsgConfirm } from '@/utils/message'
import permissionMap from '@/permission'

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
    (node.level !== 3 && permissionPrecise.value.folderCreate()) ||
    permissionPrecise.value.folderEdit() ||
    permissionPrecise.value.folderDelete()
  )
}

const { folder } = useStore()
onBeforeRouteLeave((to, from) => {
  folder.setCurrentFolder({})
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
      border-radius: var();
      color: var(--el-color-primary);
      font-weight: 500;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
    }
    &:hover {
      border-radius: var();
      background: var(--app-text-color-light-1);
    }
    &.is-active {
      &:hover {
        color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
    }
  }
  .tree-height {
    padding-top: 4px;
    height: calc(100vh - 210px);
  }
}
:deep(.overflow-inherit_node__children) {
  .el-tree-node__children {
    overflow: inherit !important;
  }
}
</style>
