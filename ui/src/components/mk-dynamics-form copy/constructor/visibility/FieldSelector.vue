<template>
  <el-cascader
    @wheel="wheel"
    :teleported="true"
    :options="options"
    v-bind="$attrs"
    v-model="data"
    separator=" > "
    clearable
  >
    <template #default="{ data }">
      <span class="flex align-center" @wheel="wheel">
        <component v-if="data.icon" :is="data.icon" class="mr-8" :size="18" :item="data" />{{
          data.label
        }}</span
      >
    </template>
  </el-cascader>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LeftOptions } from '../type'
const props = defineProps<{
  modelValue: Array<any>
  leftOptions?: Array<LeftOptions>
}>()

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
const options = computed<Array<LeftOptions>>(() => props.leftOptions ?? [])

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

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
<style scoped></style>
