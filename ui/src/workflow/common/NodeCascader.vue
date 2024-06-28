<template>
  <el-cascader
    :teleported="false"
    :options="options"
    @visible-change="visibleChange"
    v-bind="$attrs"
    v-model="data"
    separator=" > "
  >
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
import { ref, onMounted, computed } from 'vue'
import { iconComponent } from '../icons/utils'
const props = defineProps<{
  nodeModel: any
  modelValue: Array<any>
}>()
const emit = defineEmits(['update:modelValue'])
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
  },
  get: () => {
    return props.modelValue
  }
})
const options = ref<Array<any>>([])

function visibleChange(bool: boolean) {
  if (bool) {
    options.value = []
    getIncomingNode(props.nodeModel.id)
  }
}

function _getIncomingNode(id: String, startId: String) {
  let list = props.nodeModel.graphModel.getNodeIncomingNode(id)
  list = list.filter((item: any) => item.id !== startId)
  let firstElement = null
  if (list.length > 0) {
    list.forEach((item: any) => {
      if (!options.value.some((obj: any) => obj.id === item.id)) {
        options.value.unshift({
          value: item.id,
          label: item.properties.stepName,
          type: item.type,
          children: item.properties?.config?.fields || []
        })
        if (item.properties?.globalFields && item.type === 'start-node') {
          firstElement = {
            value: 'global',
            label: '全局变量',
            type: 'global',
            children: item.properties?.config?.globalFields || []
          }
        }
      }
    })

    list.forEach((item: any) => {
      _getIncomingNode(item.id, startId)
    })
  }
  if (firstElement) {
    options.value.unshift(firstElement)
  }
}
function getIncomingNode(id: string) {
  _getIncomingNode(id, id)
}
const validate = () => {
  getIncomingNode(props.nodeModel.id)
  if (!data.value) {
    return Promise.reject('引用变量必填')
  }
  if (data.value.length < 2) {
    return Promise.reject('引用变量错误')
  }
  const node_id = data.value[0]
  const node_field = data.value[1]
  const nodeParent = options.value.find((item: any) => item.value === node_id)
  if (!nodeParent) {
    return Promise.reject('不存在的引用变量')
  }
  if (!nodeParent.children.some((item: any) => item.value === node_field)) {
    return Promise.reject('不存在的引用变量')
  }
  return Promise.resolve('')
}
defineExpose({ validate })
onMounted(() => {
  getIncomingNode(props.nodeModel.id)
})
</script>
<style scoped></style>
