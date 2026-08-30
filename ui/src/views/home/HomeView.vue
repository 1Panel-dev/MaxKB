<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="px-8 py-7">
    <h1 class="text-lg">{{ route.meta.title }}</h1>
  </div>
</template>
