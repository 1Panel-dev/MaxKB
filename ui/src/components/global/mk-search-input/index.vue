<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'MkSearchInput', inheritAttrs: false })

const props = defineProps<{ placeholder?: string }>()
const searchKeyword = defineModel<string | number>({ default: '' })

defineSlots<{ append?(): unknown; prefix?(): unknown; prepend?(): unknown; suffix?(): unknown }>()
</script>

<template>
  <el-input v-model="searchKeyword" :placeholder="props.placeholder ?? t('common.actions.search')" clearable v-bind="$attrs">
    <template #prefix>
      <slot name="prefix">
        <MkIcon name="icon_search-outlined" />
      </slot>
    </template>
    <template v-if="$slots.prepend" #prepend>
      <slot name="prepend" />
    </template>
    <template v-if="$slots.append" #append>
      <slot name="append" />
    </template>
    <template v-if="$slots.suffix" #suffix>
      <slot name="suffix" />
    </template>
  </el-input>
</template>
