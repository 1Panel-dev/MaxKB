<script setup lang="ts">
defineOptions({ name: 'DynamicFormSlider' })
</script>

<template>
  <el-slider v-bind="$attrs" show-input :show-input-controls="true" />
</template>
