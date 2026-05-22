<template>
  <el-tree-select v-bind="$attrs">
    <template #header v-if="$attrs.popperHeader">
      <SelectHeader :header="$attrs.popperHeader" />
    </template>
  </el-tree-select>
</template>
<script setup lang="ts">
import SelectHeader from '@/components/dynamics-form/items/common/SelectHeader.vue'
</script>
<style lang="scss"></style>
