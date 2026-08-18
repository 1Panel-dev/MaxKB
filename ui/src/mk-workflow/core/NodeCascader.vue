<script setup lang="ts">
import type { AppNodeModel } from '@/mk-workflow/core/app-node'
import { WorkflowMode } from '@/mk-workflow/types'
import { iconComponent } from '../icons/utils'

defineOptions({ name: 'WorkflowNodeCascader', inheritAttrs: false })

interface CascaderOption {
  children?: CascaderOption[]
  label: string
  type?: string
  value: string
}

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

const props = withDefaults(
  defineProps<{
    global?: boolean
    modelValue: string[]
    nodeModel: AppNodeModel
  }>(),
  { global: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const options = ref<CascaderOption[]>([])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const getOptionsValue = () => {
  if (
    [WorkflowMode.ApplicationLoop, WorkflowMode.KnowledgeLoop, WorkflowMode.ToolLoop].includes(
      workflowMode,
    )
  ) {
    return props.global
      ? get_up_node_field_list(false, true).filter(
          (v: any) =>
            ['global', 'chat', 'output', 'loop'].includes(v.value) &&
            v.children &&
            v.children.length > 0,
        )
      : get_up_node_field_list(false, true).filter((v: any) => v.children && v.children.length > 0)
  } else {
    return props.global
      ? props.nodeModel
          .get_up_node_field_list(false, true)
          .filter(
            (v: any) =>
              ['global', 'chat', 'output'].includes(v.value) && v.children && v.children.length > 0,
          )
      : props.nodeModel
          .get_up_node_field_list(false, true)
          .filter((v: any) => v.children && v.children.length > 0)
  }
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
function refreshOptions(visible = true) {
  if (visible) options.value = getOptionsValue()
}

function validate() {
  if (selectedValue.value.length === 0) return Promise.reject('引用变量必填')
  if (selectedValue.value.length < 2) return Promise.reject('引用变量错误')

  const [nodeId, fieldValue] = selectedValue.value
  const fieldGroup = getOptionsValue().find(({ value }) => value === nodeId)
  if (!fieldGroup?.children?.some(({ value }) => value === fieldValue)) {
    selectedValue.value = []
    return Promise.reject('不存在的引用变量')
  }
  return Promise.resolve()
}

onMounted(() => {
  refreshOptions()
})
defineExpose({ validate })
</script>

<template>
  <el-cascader
    v-model="selectedValue"
    v-bind="$attrs"
    :options="options"
    :teleported="false"
    clearable
    separator=" > "
    @visible-change="refreshOptions"
    @wheel.stop
  >
    <template #default="{ node, data }">
      <span class="flex align-center" @wheel="wheel">
        <component
          :is="iconComponent(`${data.type}-icon`)"
          class="mr-8"
          :size="18"
          :item="data"
          style="--el-avatar-border-radius: 6px"
        />{{ data.label }}</span
      >
    </template>
  </el-cascader>
</template>
