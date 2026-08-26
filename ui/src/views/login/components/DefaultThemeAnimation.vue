<script setup lang="ts">
import animationMotion from '@/assets/login-theme/default.png'

defineOptions({ name: 'DefaultThemeAnimation' })
</script>

<template>
  <div class="w-full" aria-hidden="true">
    <img :src="animationMotion" alt="" class="w-full object-contain" />
  </div>
</template>
