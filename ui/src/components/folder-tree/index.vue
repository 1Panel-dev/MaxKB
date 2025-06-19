<template>
  <div class="folder-tree">
    <el-input
      v-model="filterText"
      :placeholder="$t('common.search')"
      prefix-icon="Search"
      clearable
      class="p-8"
    />
    <div
      @click="handleSharedNodeClick"
      v-if="!!shareTitle"
      class="shared-knowledge"
      :class="currentNodeKey === 'share' && 'active'"
    >
      <AppIcon :iconName="iconName" style="font-size: 18px"></AppIcon>
      <span class="ml-8 lighter">{{ $t(shareTitle) }}</span>
    </div>
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
    >
      <template #default="{ node, data }">
        <div class="flex-between w-full" @mouseenter.stop="handleMouseEnter(data)">
          <div class="flex align-center">
            <AppIcon iconName="app-folder" style="font-size: 16px"></AppIcon>
            <span class="ml-8">{{ node.label }}</span>
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
              <el-button text class="w-full">
                <el-icon class="rotate-90"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click.stop="openCreateFolder(data)">
                    <AppIcon iconName="app-add-folder"></AppIcon>
                    {{ '添加子文件夹' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click.stop="openEditFolder(data)">
                    <el-icon><EditPen /></el-icon>
                    {{ $t('common.edit') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    divided
                    @click.stop="deleteFolder(data)"
                    :disabled="data.id === 'default'"
                  >
                    <el-icon><Delete /></el-icon>
                    {{ $t('common.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>
    </el-tree>
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" :title="title" />
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import type { TreeInstance } from 'element-plus'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import { t } from '@/locales'
import folderApi from '@/api/folder'
defineOptions({ name: 'FolderTree' })
const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  currentNodeKey: {
    type: String,
    default: 'root',
  },
  source: {
    type: String,
    default: 'APPLICATION',
  },
  isShared: {
    type: Boolean,
    default: false,
  },
  iconName: {
    type: String,
    default: 'app-folder-share-active',
  },
  shareTitle: {
    type: String,
    default: 'views.system.share_knowledge',
  },
  canOperation: {
    type: Boolean,
    default: true,
  },
})
interface Tree {
  name: string
  children?: Tree[]
  id?: string
  show?: boolean
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
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

const handleNodeClick = (data: Tree) => {
  emit('handleNodeClick', data)
}

const handleSharedNodeClick = () => {
  treeRef.value?.setCurrentKey(undefined)
  emit('handleNodeClick', { id: 'share', name: t(props.shareTitle) })
}

function deleteFolder(row: Tree) {
  folderApi.delFolder(row.id as string, props.source, loading).then(() => {
    emit('refreshTree')
  })
}

const CreateFolderDialogRef = ref()
function openCreateFolder(row: Tree) {
  title.value = '添加子文件夹'
  CreateFolderDialogRef.value.open(props.source, row.id)
}
function openEditFolder(row: Tree) {
  title.value = '编辑文件夹'
  CreateFolderDialogRef.value.open(props.source, row.id, row)
}

function refreshFolder() {
  emit('refreshTree')
}
</script>
<style lang="scss" scoped>
.shared-knowledge {
  padding-left: 8px;
  display: flex;
  align-items: center;
  height: 40px;
  position: relative;
  margin-bottom: 8px;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background: var(--app-text-color-light-1);
    color: var(--el-menu-text-color);
  }

  &.active {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -4px;
    background-color: #1f232926;
    left: 0;
    width: 100%;
    height: 1px;
  }
}
:deep(.overflow-inherit_node__children) {
  .el-tree-node__children {
    overflow: inherit !important;
  }
}
</style>
