<script setup lang="ts">
import { computed } from 'vue'
import type { VisibilityFieldOption } from '../../type'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import { iconComponent } from '@/workflow-canvas/icons/utils'
const props = defineProps<{ modelValue: string[]; leftOptions?: VisibilityFieldOption[] }>()

const emit = defineEmits(['update:modelValue', 'change'])
const data = computed({
  set: (value) => {
    emit('update:modelValue', value)
    emit('change', value)
  },
  get: () => {
    return props.modelValue
  },
})
const options = computed<VisibilityFieldOption[]>(() => props.leftOptions ?? [])

const selectedNodeField = computed(() => {
  const [nodeValue, fieldValue] = data.value ?? []
  if (!nodeValue || !fieldValue) return undefined

  const fieldGroup = options.value.find((field) => field.value === nodeValue)
  return fieldGroup?.children?.some((field) => field.value === fieldValue) ? fieldGroup : undefined
})

const validate = () => {
  if (!data.value || data.value.length === 0) {
    return Promise.reject('请选择引用变量')
  }
  if (data.value.length < 2) {
    return Promise.reject('引用变量格式错误')
  }
  const [scopeValue, fieldValue] = data.value
  const scope = options.value.find((item) => item.value === scopeValue)
  if (!scope) {
    data.value = []
    return Promise.reject('未找到引用变量')
  }
  if (!scope.children?.some((child) => child.value === fieldValue)) {
    data.value = []
    return Promise.reject('未找到引用变量')
  }
  return Promise.resolve('')
}

defineExpose({ validate })
</script>

<template>
  <el-cascader class="w-full" @wheel="handleNodeWheel" :teleported="true" :options="options" v-bind="$attrs" v-model="data" separator=" > " clearable>
    <template v-if="selectedNodeField" #prefix>
      <component :is="iconComponent(`${selectedNodeField.type}-icon`)" :size="20" :item="selectedNodeField" class="small" />
    </template>
    <template #default="{ data }">
      <span class="flex items-center gap-1" @wheel="handleNodeWheel">
        <component :is="iconComponent(`${data.type}-icon`)" :size="16" :item="data" class="small" />
        <span>{{ data.label }}</span>
      </span>
    </template>
  </el-cascader>
</template>
