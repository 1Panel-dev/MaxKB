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
        <component
          :is="iconComponent(`${data.type}-icon`)"
          class="mr-8"
          :size="18"
          :item="data"
        />{{ data.label }}</span
      >
    </template>
  </el-cascader>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, inject } from 'vue'
import { iconComponent } from '../icons/utils'
import { t } from '@/locales'
import { WorkflowMode } from '@/enums/application'
const props = defineProps<{
  nodeModel: any
  modelValue: Array<any>
  global?: boolean
}>()
const emit = defineEmits(['update:modelValue'])
const workflowMode = inject('workflowMode') as WorkflowMode
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
  },
  get: () => {
    return props.modelValue
  },
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
    initOptions()
  }
}

const validate = () => {
  const incomingNodeValue = getOptionsValue()
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

const get_up_node_field_list = (contain_self: boolean, use_cache: boolean) => {
  const result = props.nodeModel.get_up_node_field_list(contain_self, use_cache)
  if (props.nodeModel.graphModel.get_up_node_field_list) {
    const _u = props.nodeModel.graphModel.get_up_node_field_list(contain_self, use_cache)

    _u.forEach((item: any) => {
      result.push(item)
    })
  }
  return result.filter((v: any) => v.children && v.children.length > 0)
}
const getOptionsValue = () => {
  if (workflowMode == WorkflowMode.ApplicationLoop) {
    return props.global
      ? get_up_node_field_list(false, true).filter(
          (v: any) =>
            ['global', 'chat', 'loop'].includes(v.value) && v.children && v.children.length > 0,
        )
      : get_up_node_field_list(false, true).filter((v: any) => v.children && v.children.length > 0)
  } else {
    return props.global
      ? props.nodeModel
          .get_up_node_field_list(false, true)
          .filter(
            (v: any) => ['global', 'chat'].includes(v.value) && v.children && v.children.length > 0,
          )
      : props.nodeModel
          .get_up_node_field_list(false, true)
          .filter((v: any) => v.children && v.children.length > 0)
  }
}
const initOptions = () => {
  options.value = getOptionsValue()
}
defineExpose({ validate })
onMounted(() => {
  initOptions()
})
</script>
<style scoped></style>
