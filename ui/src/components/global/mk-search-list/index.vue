<script setup lang="ts">
defineOptions({ name: 'MkSearchList' })

const searchKeyword = defineModel<string>({ default: '' })
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <MkSearchInput v-model="searchKeyword" class="mb-2 shrink-0" />

    <el-scrollbar class="min-h-0 flex-1">
      <slot />
    </el-scrollbar>
  </div>
</template>
