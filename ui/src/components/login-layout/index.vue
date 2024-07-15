<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <el-row class="container w-full h-full">
        <el-col :xs="0" :sm="0" :md="10" :lg="10" :xl="10" class="left-container">
          <div class="login-image">
            <img :src="`../src/assets/theme/${themeImg}.jpg`" class="login-image" />
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="14" :lg="14" :xl="14" class="right-container flex-center">
          <slot></slot>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
defineOptions({ name: 'LoginLayout' })
const props = defineProps({
  themeImg: {
    type: String,
    default: 'default'
  }
})
</script>
<style lang="scss" scope>
.login-warp {
  height: 100vh;

  .login-image {
    object-fit: cover;
    width: 100%;
    height: 100%;
  }
}
</style>
