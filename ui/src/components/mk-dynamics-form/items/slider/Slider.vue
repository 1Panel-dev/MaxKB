<script setup lang="ts">
defineOptions({ name: 'DynamicFormSlider' })
</script>

<template>
  <MkSlider v-bind="$attrs" show-input :show-input-controls="true" />
</template>
