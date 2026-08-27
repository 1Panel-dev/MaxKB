<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
import type { FormField } from '../../type'
const props = withDefaults(
  defineProps<{
    modelValue?: string[]
    formField: FormField
  }>(),
  { modelValue: () => [] },
)

defineOptions({ name: 'DynamicFormKnowledge', inheritAttrs: false })

const emit = defineEmits(['update:modelValue', 'change'])

const modelValueProxy = computed({
  get: () =>
    props.modelValue.filter((id: string) => availableList.value.some((item) => item.id === id)) ||
    [],
  set: (value: string[]) => {
    emit('update:modelValue', value)
    emit('change', props.formField)
  },
})
// 可用
const availableList = computed(() => {
  return (props.formField.attrs?.knowledge_list as DynamicFormValue[]) || []
})

const selectedIds = computed({
  get: () => modelValueProxy.value || [],
  set: (ids: string[]) => {
    modelValueProxy.value = ids
  },
})
</script>

<template>
  <div class="w-full">
    <el-select
      v-model="selectedIds"
      multiple
      v-bind="$attrs"
      class="w-full"
      placeholder="请选择知识库"
    >
      <el-option v-for="item in availableList" :key="item.id" :label="item.name" :value="item.id">
        <el-space :size="8">
          <KnowledgeIcon :type="item.type" :size="20" style="--el-avatar-border-radius: 6px" />
          <span>{{ item.name }}</span>
        </el-space>
      </el-option>
      <template #label="{ label, value }">
        <el-space :size="8">
          <KnowledgeIcon
            :type="availableList.find((item) => item.id === value)?.type"
            :size="14"
            style="--el-avatar-border-radius: 4px"
          />
          <span>{{ label }}</span>
        </el-space>
      </template>
    </el-select>
  </div>
</template>
