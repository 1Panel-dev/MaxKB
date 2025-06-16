<template>
  <div>
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
      node-key="id"
    >
      <template #default="{ node, data }">
        <div class="custom-tree-node flex align-center">
          <AppIcon iconName="app-folder" style="font-size: 16px"></AppIcon>
          <span class="ml-8">{{ node.label }}</span>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import type { TreeInstance } from 'element-plus'
import { t } from '@/locales'
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
})
interface Tree {
  name: string
  children?: Tree[]
  id?: string
}

const defaultProps = {
  children: 'children',
  label: 'name',
}

const emit = defineEmits(['handleNodeClick'])

const treeRef = ref<TreeInstance>()
const filterText = ref('')

watch(filterText, (val) => {
  treeRef.value!.filter(val)
})

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
</style>
