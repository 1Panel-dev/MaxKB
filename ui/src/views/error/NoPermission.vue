<template>
  <div class="flex-center mt-24">
    <div>
      <img src="@/assets/500.png" width="250" alt="" />
      <h4 class="text-center">{{ $t('common.notFound.NoPermission') }}</h4>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<style lang="scss" scoped></style>
