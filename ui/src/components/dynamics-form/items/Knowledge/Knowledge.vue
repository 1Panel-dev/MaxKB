<template>
  <div class="w-full">
    <el-select
      v-model="selectedIds"
      multiple
      class="w-full"
      :placeholder="$t('views.chatLog.selectKnowledgePlaceholder')"
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
            :type="relatedObject(availableList, value, 'id')?.type"
            :size="14"
            style="--el-avatar-border-radius: 4px"
          />
          <span>{{ label }}</span>
        </el-space>
      </template>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FormField } from '../../type'
import { relatedObject } from '@/utils/array'
const props = withDefaults(
  defineProps<{
    modelValue?: string[]
    formField: FormField
  }>(),
  { modelValue: () => [] },
)

const emit = defineEmits(['update:modelValue', 'change'])

const model_value = computed({
  get: () => props.modelValue || [],
  set: (value: string[]) => {
    emit('update:modelValue', value)
    emit('change', props.formField)
  },
})

const availableList = computed(() => {
  return (props.formField.attrs?.knowledge_list as any[]) || []
})

const selectedIds = computed({
  get: () => model_value.value || [],
  set: (ids: string[]) => {
    model_value.value = ids
  },
})
</script>
<style lang="scss" scoped></style>
