<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <!-- v-if="screenWidth && screenWidth >= 990" -->
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-image"></div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14" class="right-container flex-center">
          <slot></slot>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
// import { ref, onMounted } from 'vue'
// import type { Ref } from 'vue'
defineOptions({ name: 'LoginLayout' })
// const screenWidth: Ref<number | null> = ref(null)
// onMounted(() => {
//   screenWidth.value = document.body.clientWidth
//   window.onresize = () => {
//     return (() => {
//       screenWidth.value = document.body.clientWidth
//     })()
//   }
// })
</script>
<style lang="scss" scope>
.login-warp {
  height: 100vh;

  .login-image {
    background: url(@/assets/login.jpg) no-repeat center;
    background-size: cover;
    width: 100%;
    height: 100%;
  }
}
</style>
