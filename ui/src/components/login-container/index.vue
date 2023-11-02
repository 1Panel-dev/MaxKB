<template>
  <div class="login-form-container">
    <div class="login-title">
      <div class="title flex-center">
        <div class="logo"></div>
        <div class="app-logo-font">{{ title || defaultTitle }}</div>
      </div>
      <div class="sub-title" v-if="subTitle">{{ subTitle }}</div>
    </div>
    <slot></slot>
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
  width: 420px;

  .login-title {
    margin-bottom: 30px;

    .title {
      font-size: 28px;
      height: 60px;
      .logo {
        background-image: url('@/assets/logo.png');
        background-size: 100% 100%;
        width: 48px;
        height: 48px;
      }
    }

    .sub-title {
      text-align: center;
      color: #101010;
      font-size: 18px;
    }
  }
}
</style>
