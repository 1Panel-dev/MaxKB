<script setup lang="ts">
defineOptions({ name: 'MkSourceCardAction' })

defineSlots<{ default: () => unknown }>()
</script>

<template>
  <div class="group-hover-visible ml-auto flex-align-center shrink-0 gap-2" @click.stop @keydown.stop>
    <slot />
  </div>
</template>
