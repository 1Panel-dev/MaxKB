<template>
  <div class="w-full">
    <el-select
      v-model="selectedIds"
      multiple
      class="w-full"
      :placeholder="$t('dynamicsForm.Knowledge.placeholder', '请选择知识库')"
    >
      <el-option v-for="item in availableList" :key="item.id" :label="item.name" :value="item.id">
        <div class="flex align-center">
          <KnowledgeIcon :type="item.type" class="mr-8" :size="20" />
          <span>{{ item.name }}</span>
        </div>
      </el-option>
      <template #tag>
        <el-tag
          v-for="item in selectedItems"
          :key="item.id"
          closable
          type="info"
          @close="removeItem(item.id)"
          style="margin-right: 4px"
        >
          <div class="flex align-center">
            <KnowledgeIcon :type="item.type" class="mr-4" :size="16" />
            <span>{{ item.name }}</span>
          </div>
        </el-tag>
      </template>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FormField } from '../../type'

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

const selectedItems = computed(() => {
  return availableList.value.filter((k: any) => selectedIds.value.includes(k.id))
})

const selectedIds = computed({
  get: () => model_value.value || [],
  set: (ids: string[]) => {
    model_value.value = ids
  },
})

function removeItem(id: string) {
  model_value.value = model_value.value.filter((item_id: string) => item_id !== id)
}
</script>
<style lang="scss" scoped></style>
