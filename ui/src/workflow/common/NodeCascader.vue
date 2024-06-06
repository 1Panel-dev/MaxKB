<template>
  <el-cascader :options="options" @visible-change="visibleChange" v-bind="$attrs" separator=" > ">
    <template #default="{ node, data }">
      <span>{{ data.label }}</span>
    </template>
  </el-cascader>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
const props = defineProps<{
  nodeModel: any
}>()

const options = ref([])

function visibleChange(bool: boolean) {
  if (bool) {
    options.value = []
    getIncomingNode(props.nodeModel.id)
  }
}

function getIncomingNode(id: string) {
  const list = props.nodeModel.graphModel.getNodeIncomingNode(id)
  if (list.length > 0) {
    list.forEach((item) => {
      if (!options.value.some((obj: any) => obj.id === item.id)) {
        options.value.unshift({
          value: item.id,
          label: item.properties.stepName,
          children: item.properties?.fields || []
        })
      }
    })
    list.forEach((item) => {
      getIncomingNode(item.id)
    })
  }
}
</script>
<style scoped></style>
