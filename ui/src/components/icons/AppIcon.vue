<template>
  <component :is="Object.keys(iconMap).includes(iconName) ? iconMap[iconName].iconReader() : iconMap['404'].iconReader()">
  </component>
</template>
<script setup lang="ts">
import { iconMap } from "@/components/icons/index"
defineOptions({ name: 'AppIcon' });
withDefaults(defineProps<{
  iconName?: string;
}>(), {
  iconName: '404'
});



</script>
<style lang="scss" scoped></style>
