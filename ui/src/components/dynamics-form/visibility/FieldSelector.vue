<template>
  <el-cascader
    @wheel="wheel"
    :teleported="true"
    :options="options"
    @visible-change="visibleChange"
    v-bind="$attrs"
    v-model="data"
    separator=" > "
    clearable
  >
    <template #default="{ node, data }">
      <span class="flex align-center" @wheel="wheel">
        <component
          v-if="data.type"
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
import { iconComponent } from '@/workflow/icons/utils'
import { t } from '@/locales'
import { WorkflowMode } from '@/enums/application'
const props = defineProps<{
  nodeModel: any
  modelValue: Array<any>
  global?: boolean
  currentNodeFields?: Array<any>
  currentEditingIndex?: number
  excludeFieldName?: string
}>()

const emit = defineEmits(['update:modelValue', 'change'])
const workflowMode = inject('workflowMode') as WorkflowMode
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
    emit('change', value)
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
    return Promise.reject(t('workflow.variable.ReferencingRequired'))
  }
  if (data.value.length < 2) {
    return Promise.reject(t('workflow.variable.ReferencingError'))
  }
  const node_id = data.value[0]
  const node_field = data.value[1]
  const nodeParent = incomingNodeValue.find((item: any) => item.value === node_id)
  if (!nodeParent) {
    data.value = []
    return Promise.reject(t('workflow.variable.NoReferencing'))
  }
  if (!nodeParent.children.some((item: any) => item.value === node_field)) {
    data.value = []
    return Promise.reject(t('workflow.variable.NoReferencing'))
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

const injectDraftSiblings = (rawList: Array<any>) => {
  const currentNodeId = props.nodeModel?.id

  const draftSiblings = (props.currentNodeFields ?? [])
    .filter((f: any, idx: number) => {
      if (props.currentEditingIndex != null && idx >= props.currentEditingIndex) return false
      if (props.excludeFieldName && f.field === props.excludeFieldName) return false
      return true
    })
    .map((f: any) => ({
      label: typeof f.label === 'string' ? f.label : f.label?.label,
      value: f.field,
    }))
  // 将 draft parameter 转换成 cascader 适配的 {label, value} 格式

  // base-node
  const excludeSet = new Set(
    (props.currentNodeFields ?? [])
      .filter((f: any, idx: number) => {
        if (props.currentEditingIndex != null && idx >= props.currentEditingIndex) return true
        if (props.excludeFieldName && f.field === props.excludeFieldName) return true
        return false
      })
      .map((f: any) => f.field),
  )

  return rawList
    .map((entry: any) => {
      const isCurrentNode =
        entry.value === currentNodeId || (currentNodeId === 'base-node' && entry.value === 'global')
      if (!isCurrentNode) return entry

      return {
        ...entry,
        children:
          currentNodeId === 'base-node'
            ? (entry.children || []).filter((c: any) => !excludeSet.has(c.value))
            : draftSiblings,
      }
    })
    .filter((entry: any) => entry.children && entry.children.length > 0)
}

const getOptionsValue = () => {
  if (!props.nodeModel) return []
  if (
    [WorkflowMode.ApplicationLoop, WorkflowMode.KnowledgeLoop, WorkflowMode.ToolLoop].includes(
      workflowMode,
    )
  ) {
    const list = props.global
      ? get_up_node_field_list(true, true).filter(
          (v: any) =>
            ['global', 'chat', 'output', 'loop'].includes(v.value) &&
            v.children &&
            v.children.length > 0,
        )
      : get_up_node_field_list(true, true)
    return injectDraftSiblings(list)
  }

  const raw = props.nodeModel.get_up_node_field_list(true, true)
  const list = props.global
    ? raw.filter(
        (v: any) =>
          ['global', 'chat', 'output'].includes(v.value) && v.children && v.children.length > 0,
      )
    : raw.filter((v: any) => v.children && v.children.length > 0)
  return injectDraftSiblings(list)
}

const initOptions = () => {
  if (!props.nodeModel) return
  const next = getOptionsValue()
  if (JSON.stringify(options.value) === JSON.stringify(next)) return

  options.value = next
}
defineExpose({ validate })
onMounted(() => {
  initOptions()
})
</script>
<style scoped></style>
