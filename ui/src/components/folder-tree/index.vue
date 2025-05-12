<template>
  <div>
    <el-input
      v-model="filterText"
      :placeholder="$t('common.search')"
      prefix-icon="Search"
      clearable
      class="p-8"
    />
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
          <span class="ml-8" >{{ node.label }}</span>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import type { TreeInstance } from 'element-plus'
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
})
interface Tree {
  name: string
  children?: Tree[]
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
</script>
