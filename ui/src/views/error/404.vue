<template>
  <div class="not-found-container flex-center">
    <div>
      <img src="@/assets/404.png" width="250" alt="" />
      <h4 class="text-center">{{ $t('common.notFound.title') }}</h4>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<style lang="scss" scoped>
.not-found-container {
  height: 100vh;
  width: 100vw;
}
</style>
