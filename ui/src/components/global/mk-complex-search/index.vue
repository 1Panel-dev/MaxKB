<script setup lang="ts">
import { computed, watch } from 'vue'
import type { ComplexSearchFieldOption, ComplexSearchValue } from '@/types'

defineOptions({ name: 'MkComplexSearch' })

const props = withDefaults(
  defineProps<{
    fields: ComplexSearchFieldOption[]
  }>(),
  {},
)

const searchValue = defineModel<ComplexSearchValue | undefined>('')
const searchField = defineModel<string>('field', { required: true })
const emit = defineEmits<{
  change: [value: ComplexSearchValue | undefined]
  fieldChange: [field: string]
}>()

const activeField = computed(() => props.fields.find(({ value }) => value === searchField.value))
const inputValue = computed<number | string>({
  get: () => {
    return typeof searchValue.value === 'boolean' ? '' : (searchValue.value ?? '')
  },
  set: (value) => {
    searchValue.value = value
  },
})

watch(searchField, (field) => {
  searchValue.value = ''
  emit('fieldChange', field)
  emit('change', '')
})
</script>

<template>
  <div class="mk-complex-search flex">
    <el-select v-model="searchField" class="mk-complex-search__field w-23!">
      <el-option
        v-for="field in fields"
        :key="field.value"
        :label="field.label"
        :value="field.value"
      />
    </el-select>

    <el-select
      v-if="activeField?.type === 'select'"
      :key="activeField.value"
      v-model="searchValue"
      class="mk-complex-search__value w-50!"
      clearable
      placeholder="请选择"
      @change="emit('change', $event)"
    >
      <el-option
        v-for="option in activeField.options ?? []"
        :key="String(option.value)"
        :disabled="option.disabled"
        :label="option.label"
        :value="option.value"
      />
    </el-select>

    <el-input
      v-else
      :key="activeField?.value"
      v-model="inputValue"
      class="mk-complex-search__value w-50!"
      clearable
      placeholder="请输入"
      @change="emit('change', $event)"
    />
  </div>
</template>

<style scoped lang="scss">
.mk-complex-search {
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  &__field {
    border-right: 1px solid var(--el-border-color);
    :deep(.el-select__wrapper) {
      box-shadow: none !important;
      border-radius: var(--el-border-radius-base) 0 0 var(--el-border-radius-base);
    }
  }

  &__value {
    :deep(.el-select__wrapper) {
      box-shadow: none !important;
      border-radius: 0 var(--el-border-radius-base) var(--el-border-radius-base) 0;
      min-height: 30px !important;
    }
    :deep(.el-input__wrapper) {
      box-shadow: none !important;
      border-radius: 0 var(--el-border-radius-base) var(--el-border-radius-base) 0;
    }
  }
}
</style>
