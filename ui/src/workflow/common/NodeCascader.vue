<template>
  <el-cascader
    @wheel="wheel"
    :teleported="false"
    :options="options"
    @visible-change="visibleChange"
    v-bind="$attrs"
    v-model="data"
    separator=" > "
  >
    <template #default="{ node, data }">
      <span class="flex align-center" @wheel="wheel">
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
import { t } from '@/locales'
const props = defineProps<{
  nodeModel: any
  modelValue: Array<any>
  global?: Boolean
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

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

function visibleChange(bool: boolean) {
  if (bool) {
    options.value = props.global
      ? props.nodeModel.get_up_node_field_list(false, true).filter((v: any) => v.value === 'global')
      : props.nodeModel.get_up_node_field_list(false, true)
  }
}

const validate = () => {
  const incomingNodeValue = props.nodeModel.get_up_node_field_list(false, true)
  if (!data.value || data.value.length === 0) {
    return Promise.reject(t('views.applicationWorkflow.variable.ReferencingRequired'))
  }
  if (data.value.length < 2) {
    return Promise.reject(t('views.applicationWorkflow.variable.ReferencingError'))
  }
  const node_id = data.value[0]
  const node_field = data.value[1]
  const nodeParent = incomingNodeValue.find((item: any) => item.value === node_id)
  if (!nodeParent) {
    data.value = []
    return Promise.reject(t('views.applicationWorkflow.variable.NoReferencing'))
  }
  if (!nodeParent.children.some((item: any) => item.value === node_field)) {
    data.value = []
    return Promise.reject(t('views.applicationWorkflow.variable.NoReferencing'))
  }
  return Promise.resolve('')
}
defineExpose({ validate })
onMounted(() => {
  options.value = props.global
    ? props.nodeModel.get_up_node_field_list(false, true).filter((v: any) => v.value === 'global')
    : props.nodeModel.get_up_node_field_list(false, true)
})
</script>
<style scoped></style>
