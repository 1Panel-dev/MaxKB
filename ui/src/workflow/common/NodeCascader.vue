<template>
  <el-cascader :options="options" @visible-change="visibleChange" v-bind="$attrs" separator=" > ">
    <template #default="{ node, data }">
      <span class="flex align-center">
        <component :is="iconComponent(`${data.type}-icon`)" class="mr-8" :size="18" />{{
          data.label
        }}</span
      >
    </template>
  </el-cascader>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { iconComponent } from '../icons/utils'
const props = defineProps<{
  nodeModel: any
}>()

const options = ref<Array<any>>([])

function visibleChange(bool: boolean) {
  if (bool) {
    options.value = []
    getIncomingNode(props.nodeModel.id)
  }
}

function getIncomingNode(id: string) {
  const list = props.nodeModel.graphModel.getNodeIncomingNode(id)
  if (list.length > 0) {
    list.forEach((item: any) => {
      if (!options.value.some((obj: any) => obj.id === item.id)) {
        options.value.unshift({
          value: item.id,
          label: item.properties.stepName,
          type: item.type,
          children: item.properties?.fields || []
        })
      }
    })
    list.forEach((item: any) => {
      getIncomingNode(item.id)
    })
  }
}
</script>
<style scoped></style>
