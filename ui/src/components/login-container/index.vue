<template>
  <div class="login-form-container">
    <div class="login-title">
      <div class="logo text-center">
        <LogoFull height="45px" />
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
