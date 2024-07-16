<template>
  <div class="login-preview mr-16">
    <div class="header">
      <div class="tag flex-between">
        <div class="flex align-center">
          <img v-if="props.data.icon" :src="fileURL" alt="" height="20px" class="mr-8" />
          <img v-else src="@/assets/logo/logo.svg" height="24px" class="mr-8" />
          <span class="ellipsis">{{ data.title }}</span>
        </div>
        <el-icon><Close /></el-icon>
      </div>
    </div>
    <login-layout style="height: 530px">
      <LoginContainer :subTitle="data.slogan" class="login-container">
        <div class="mask"></div>
        <h2 class="mb-24">{{ '普通登录' }}</h2>
        <el-form class="login-form">
          <div class="mb-24">
            <el-form-item>
              <el-input size="large" class="input-item" placeholder="请输入用户名"> </el-input>
            </el-form-item>
          </div>
          <div class="mb-24">
            <el-form-item>
              <el-input
                type="password"
                size="large"
                class="input-item"
                placeholder="请输入密码"
                show-password
              >
              </el-input>
            </el-form-item>
          </div>
        </el-form>
        <el-button size="large" type="primary" class="w-full">登录</el-button>
        <div class="operate-container flex-between mt-12">
          <el-button class="forgot-password" link type="primary"> 忘记密码? </el-button>
        </div>
      </LoginContainer>
    </login-layout>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  }
})

const fileURL = computed(() => {
  if (props.data.icon) {
    if (typeof props.data.icon === 'string') {
      return props.data.icon
    } else {
      return URL.createObjectURL(props.data.icon)
    }
  } else {
    return ''
  }
})
</script>

<style lang="scss" scoped>
.login-preview {
  background: #ffffff;
  border-radius: 4px;
  transform-origin: center;
  .login-container {
    transform: translate(0, 0) scale(0.8);
    position: relative;
    .mask {
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 100%;
      z-index: 3;
    }
  }

  .header {
    background: #eff0f1;
    height: 38px;
    border-radius: 4px 4px 0 0;
    position: relative;
    .tag {
      width: 180px;
      height: 30px;
      background: #ffffff;
      box-shadow: var(-app-text-color-light-1);
      position: absolute;
      bottom: 0;
      left: 8px;
      border-radius: 4px 4px 0 0;
      padding: 0 8px;
    }
  }
}
</style>
