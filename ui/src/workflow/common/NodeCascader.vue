<template>
  <el-cascader
    @wheel="wheel"
    @keydown="isKeyDown = true"
    @keyup="isKeyDown = false"
    :teleported="false"
    :options="options"
    @visible-change="visibleChange"
    v-bind="$attrs"
    v-model="data"
    separator=" > "
  >
    <template #default="{ node, data }">
      <span
        class="flex align-center"
        @wheel="wheel"
        @keydown="isKeyDown = true"
        @keyup="isKeyDown = false"
      >
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
const isKeyDown = ref(false)
const wheel = (e: any) => {
  if (isKeyDown.value) {
    e.preventDefault()
  } else {
    e.stopPropagation()
    return true
  }
}

function visibleChange(bool: boolean) {
  if (bool) {
    options.value = getIncomingNode(props.nodeModel.id)
  }
}

function _getIncomingNode(id: String, startId: String, value: Array<any>) {
  let list = props.nodeModel.graphModel.getNodeIncomingNode(id)
  list = list.filter((item: any) => item.id !== startId)
  let firstElement = null
  if (list.length > 0) {
    list.forEach((item: any) => {
      if (!value.some((obj: any) => obj.id === item.id)) {
        value.unshift({
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
      _getIncomingNode(item.id, startId, value)
    })
  }
  if (firstElement) {
    value.unshift(firstElement)
  }
  return value
}
function getIncomingNode(id: string) {
  return _getIncomingNode(id, id, [])
}
const validate = () => {
  const incomingNodeValue = getIncomingNode(props.nodeModel.id)
  options.value = incomingNodeValue
  if (!data.value || data.value.length === 0) {
    return Promise.reject('引用变量必填')
  }
  if (data.value.length < 2) {
    return Promise.reject('引用变量错误')
  }
  const node_id = data.value[0]
  const node_field = data.value[1]
  const nodeParent = incomingNodeValue.find((item: any) => item.value === node_id)
  if (!nodeParent) {
    data.value = []
    return Promise.reject('不存在的引用变量')
  }
  if (!nodeParent.children.some((item: any) => item.value === node_field)) {
    data.value = []
    return Promise.reject('不存在的引用变量')
  }
  return Promise.resolve('')
}
defineExpose({ validate })
onMounted(() => {
  options.value = getIncomingNode(props.nodeModel.id)
})
</script>
<style scoped></style>
