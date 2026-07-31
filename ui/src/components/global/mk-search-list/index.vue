<script setup lang="ts">
defineOptions({ name: 'MkSearchList' })

withDefaults(
  defineProps<{
    placeholder?: string
  }>(),
  {
    placeholder: '搜索',
  },
)

const searchKeyword = defineModel<string>({ default: '' })
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <el-input v-model="searchKeyword" clearable :placeholder="placeholder" class="mb-2 shrink-0">
      <template #prefix>
        <MkIcon name="icon_search-outlined" />
      </template>
    </el-input>

    <el-scrollbar class="min-h-0 flex-1">
      <slot />
    </el-scrollbar>
  </div>
</template>
