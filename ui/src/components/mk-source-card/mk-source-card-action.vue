<script setup lang="ts">
defineOptions({ name: 'MkSourceCardAction' })

defineSlots<{
  default: () => unknown
}>()
</script>

<template>
  <div
    class="pointer-events-none ml-auto flex shrink-0 items-center gap-2 opacity-0 transition-opacity group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100"
    @click.stop
    @keydown.stop
  >
    <slot />
  </div>
</template>
