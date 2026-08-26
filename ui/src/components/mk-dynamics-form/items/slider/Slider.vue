<script setup lang="ts">
defineOptions({ name: 'DynamicFormSlider' })
</script>

<template>
  <el-slider v-bind="$attrs" show-input :show-input-controls="false" class="custom-slider" />
</template>
