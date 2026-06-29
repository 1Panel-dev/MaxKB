<template>
  <div class="login-form-container p-24">
    <div class="login-title-section">
      <div class="mobile-logo text-center" v-if="!theme.themeInfo?.loginLogo">
        <img src="@/assets/logo/logo.png" alt="logo" class="mobile-logo-img" />
      </div>
      <div class="logo text-center" v-else>
        <slot name="logo">
          <LogoFull height="45px" />
        </slot>
      </div>
      <div class="sub-title text-center" v-if="subTitle">
        <el-text type="info">{{ subTitle }}</el-text>
      </div>
    </div>
    <div class="login-glass-card">
      <slot></slot>
    </div>
  </div>
</template>
<script setup lang="ts">
import useStore from '@/stores'

defineProps({
  title: String,
  subTitle: String,
})

const { theme } = useStore()
</script>
<style lang="scss" scoped>
.login-form-container {
  width: 480px;

  .login-title-section {
    margin-bottom: 32px;
    .sub-title {
      font-size: 16px;
      color: var(--text-secondary);
    }
  }
}

.mobile-logo-img {
  height: 40px;
  width: auto;
}

.login-glass-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--app-border-radius-xlarge);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  padding: 32px;
}

[data-theme="dark"] .login-glass-card {
  background: rgba(44, 44, 46, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
</style>
