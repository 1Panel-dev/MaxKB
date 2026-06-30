·
<template>
  <div class="app-top-bar-container flex-center">
    <div class="logo-container flex align-center">
      <img src="@/assets/logo/inspur_logo.png" alt="logo" class="header-logo" />
    </div>

    <div class="flex-between w-full align-center">
      <h4><el-divider class="ml-16 mr-16" direction="vertical" />{{ $t('views.system.title') }}</h4>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import Avatar from './avatar/index.vue'
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}

.logo-container {
  gap: 10px;
}

.header-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}
</style>
