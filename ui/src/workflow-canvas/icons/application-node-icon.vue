<script setup lang="ts">
const props = defineProps<{
  item: {
    name: string
    icon: string
  }
  size?: string | number
}>()
</script>
<template>
  <ApplicationIcon :icon="props.item.icon" />
</template>
