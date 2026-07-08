<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <div class="flex-center w-full h-full">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;
  background: url('@/assets/chat/user-login-bg.png') var(--app-layout-bg-color) no-repeat center;
}
</style>
