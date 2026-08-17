<script setup lang="ts">
import { computed } from 'vue'
import type { OptionItem } from '@/api/types'

defineOptions({ name: 'MkComplexSearch' })

interface ComplexSearchField extends OptionItem<string> {
  remoteMethod?: (query: string) => Promise<unknown> | void
}

const props = withDefaults(
  defineProps<{
    fields: ComplexSearchField[]
  }>(),
  {},
)
const emit = defineEmits<{
  change: [value: Record<string, boolean | number | string> | undefined]
}>()

// 异步搜索
const remoteLoading = ref(false)
let remoteRequestId = 0
function handleRemoteSearch(query: string) {
  const request = activeField.value?.remoteMethod?.(query)
  if (!(request instanceof Promise)) return

  const requestId = ++remoteRequestId
  remoteLoading.value = true
  request.then(
    () => {
      if (requestId === remoteRequestId) remoteLoading.value = false
    },
    () => {
      if (requestId === remoteRequestId) remoteLoading.value = false
    },
  )
}

const searchValue = ref('')
const searchField = ref(props.fields[0]?.value ?? '')

const activeField = computed(() => props.fields.find(({ value }) => value === searchField.value))

function handleFieldChange() {
  const shouldClearSearch = searchValue.value !== '' && searchValue.value !== undefined
  remoteRequestId += 1
  remoteLoading.value = false
  searchValue.value = ''
  if (shouldClearSearch) emit('change', undefined)
}

function handleChange() {
  if (searchValue.value === '' || searchValue.value === undefined) {
    emit('change', undefined)
  } else {
    emit('change', { [searchField.value]: searchValue.value })
  }
}
</script>

<template>
  <div class="mk-complex-search flex">
    <el-select
      v-model="searchField"
      class="mk-complex-search__field w-26!"
      @change="handleFieldChange"
      :persistent="false"
    >
      <el-option
        v-for="field in fields"
        :key="field.value"
        :label="field.label"
        :value="field.value"
      />
    </el-select>

    <el-select
      v-if="activeField?.options"
      :key="activeField.value"
      v-model="searchValue"
      class="mk-complex-search__value w-50!"
      clearable
      :loading="remoteLoading"
      placeholder="请选择"
      filterable
      reserve-keyword
      :remote="Boolean(activeField.remoteMethod)"
      :remote-method="handleRemoteSearch"
      @change="handleChange"
      :persistent="false"
    >
      <el-option
        v-for="(option, index) in activeField.options ?? []"
        :key="index"
        :disabled="option.disabled"
        :label="option.label"
        :value="option.value"
      />
    </el-select>

    <el-input
      v-else
      :key="activeField?.value"
      v-model="searchValue"
      class="mk-complex-search__value w-50!"
      clearable
      placeholder="请输入"
      @change="handleChange"
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
      min-height: 30px !important;
    }
  }

  &__value {
    :deep(.el-select__wrapper) {
      box-shadow: none !important;
      border-radius: 0 var(--el-border-radius-base) var(--el-border-radius-base) 0;
      min-height: 30px !important;
    }
    --el-input-inner-height: 28px !important;
    :deep(.el-input__wrapper) {
      box-shadow: none !important;
      border-radius: 0 var(--el-border-radius-base) var(--el-border-radius-base) 0;
    }
  }
}
</style>
