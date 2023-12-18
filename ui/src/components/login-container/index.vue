<template>
  <div class="login-form-container">
    <div class="login-title">
      <div class="title flex-center mb-8">
        <div class="logo mr-4"></div>
        <div class="app-logo-font">{{ title || defaultTitle }}</div>
      </div>
      <div class="sub-title text-center" v-if="subTitle">
        <el-text type="info">{{ subTitle }}</el-text>
      </div>
    </div>
    <el-card class="login-card">
      <slot></slot>
    </el-card>
  </div>
</template>
<script setup lang="ts">
const defaultTitle = import.meta.env.VITE_APP_TITLE
defineOptions({ name: 'LoginContainer' })
defineProps({
  title: String,
  subTitle: String
})
</script>
<style lang="scss" scope>
.login-form-container {
  width: 480px;

  .login-title {
    margin-bottom: 32px;

    .title {
      font-size: 32px;
      .logo {
        background-image: url('@/assets/logo.png');
        background-size: 100% 100%;
        width: 45px;
        height: 45px;
      }
    }
    .sub-title {
      font-size: 16px;
    }
  }
  .login-card {
    border-radius: 8px;
    padding: 18px;
  }
}
</style>
