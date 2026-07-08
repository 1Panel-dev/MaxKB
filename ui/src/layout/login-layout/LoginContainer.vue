<template>
  <div class="login-form-container p-24">
    <div class="login-title">
      <div class="logo text-center">
        <slot name="logo">
          <LogoFull height="45px" />
        </slot>
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
defineProps({
  title: String,
  subTitle: String,
})
</script>
<style lang="scss" scoped>
.login-form-container {
  width: 480px;


  .login-title {
    margin-bottom: 32px;
    .sub-title {
      font-size: 16px;
    }
  }
  .login-card {
    padding: 18px;
  }
}
</style>
