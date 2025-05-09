<template>
  <el-tree
    style="max-width: 600px"
    :data="data"
    :props="defaultProps"
    @node-click="handleNodeClick"
  />
</template>

<script lang="ts" setup>
defineOptions({ name: 'FolderTree' })
const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})
interface Tree {
  name: string
  children?: Tree[]
}

const handleNodeClick = (data: Tree) => {
  console.log(data)
}

const defaultProps = {
  children: 'children',
  label: 'name',
}
</script>
