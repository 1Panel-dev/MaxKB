<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OptionItem } from '@/api/types'

defineOptions({ name: 'MkComplexSearch' })

const { t } = useI18n({ useScope: 'global' })

interface ComplexSearchField extends OptionItem<string> {
  multiple?: boolean
  remoteMethod?: (query: string) => Promise<unknown> | void
}

type SearchValue = boolean | number | string

const props = withDefaults(defineProps<{ fields: ComplexSearchField[] }>(), {})
const emit = defineEmits<{ change: [value: Record<string, SearchValue | SearchValue[]> | undefined] }>()

// 异步搜索
const remoteLoading = ref(false)
function handleRemoteSearch(query: string) {
  const request = activeField.value?.remoteMethod?.(query)
  if (!(request instanceof Promise)) return

  remoteLoading.value = true
  request.then(
    () => {
      remoteLoading.value = false
    },
    () => {
      remoteLoading.value = false
    },
  )
}

const searchField = ref(props.fields[0]?.value ?? '')
const searchValue = ref<SearchValue | SearchValue[]>(props.fields[0]?.multiple ? [] : '')

const activeField = computed(() => props.fields.find(({ value }) => value === searchField.value))

function handleFieldChange() {
  const shouldClearSearch = Array.isArray(searchValue.value) ? searchValue.value.length > 0 : searchValue.value !== ''

  remoteLoading.value = false
  searchValue.value = activeField.value?.multiple ? [] : ''
  if (shouldClearSearch) emit('change', undefined)
}

function handleChange() {
  if (searchValue.value === '' || (Array.isArray(searchValue.value) && !searchValue.value.length)) {
    emit('change', undefined)
  } else {
    emit('change', { [searchField.value]: searchValue.value })
  }
}
</script>

<template>
  <div class="mk-input-group">
    <!-- 选择搜索字段 -->
    <el-select v-model="searchField" class="mk-input-group__prepend w-26!" @change="handleFieldChange" :persistent="false">
      <el-option v-for="field in fields" :key="field.value" :label="field.label" :value="field.value" />
    </el-select>

    <!-- 选择搜索条件 -->
    <el-select
      v-if="activeField?.options"
      :key="activeField.value"
      v-model="searchValue"
      class="mk-input-group__content w-50!"
      clearable
      :loading="remoteLoading"
      :multiple="activeField.multiple"
      :placeholder="t('common.placeholders.select')"
      filterable
      collapse-tags
      collapse-tags-tooltip
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

    <!-- 输入搜索条件 -->
    <el-input
      v-else
      :key="activeField?.value"
      v-model="searchValue"
      class="mk-input-group__content w-50!"
      clearable
      :placeholder="t('common.placeholders.input')"
      @change="handleChange"
    />
  </div>
</template>
