<template>
  <el-breadcrumb separator-icon="ArrowRight" style="line-height: 22px">
    <h2 v-if="breadcrumbData?.length === 1" class="ellipsis" :title="breadcrumbData[0]?.name">
      {{ breadcrumbData[0]?.name }}
    </h2>
    <el-breadcrumb-item v-for="(item, index) in breadcrumbData" :key="index" v-else>
      <h5 class="ml-4 ellipsis" v-if="index === breadcrumbData.length - 1" :title="item.name">
        {{ item.name }}
      </h5>
      <el-button v-else link @click="handleClick(item)" :title="item.name">
        <span class="ellipsis"> {{ item.name }}</span>
      </el-button>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TreeToFlatten } from '@/utils/array'
defineOptions({ name: 'FolderBreadcrumb' })
import useStore from '@/stores'
const { folder, user } = useStore()

const props = defineProps({
  folderList: {
    type: Array,
    default: () => [],
  },
})

const breadcrumbData = computed(() => {
  return folder.currentFolder?.id && getBreadcrumbData()
})

const emit = defineEmits(['click'])

function getBreadcrumbData() {
  const targetId = folder.currentFolder?.id
  const list = TreeToFlatten(props.folderList)
  if (!folder.currentFolder) return [] // 如果没有 id，返回空数组
  const breadcrumbList: any[] = []
  let currentId: string | null = targetId
  while (currentId) {
    const currentNode = list.find((item: any) => item.id === currentId)
    if (!currentNode) break // 如果找不到节点，终止循环
    breadcrumbList.unshift(currentNode) // 添加到面包屑
    currentId = currentNode.parent_id // 继续查找父级
  }
  return breadcrumbList
}

function handleClick(item: any) {
  emit('click', item)
}
</script>

<style lang="scss" scoped></style>
