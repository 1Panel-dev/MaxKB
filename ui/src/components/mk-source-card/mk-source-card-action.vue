<script setup lang="ts">
defineOptions({ name: 'MkSourceCardAction' })

defineSlots<{ default: () => unknown }>()
</script>

<template>
  <div class="group-hover-visible ml-auto flex shrink-0 items-center gap-2" @click.stop @keydown.stop>
    <slot />
  </div>
</template>
