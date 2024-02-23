<template>
  <el-dialog v-model="aboutDialogVisible" class="about-dialog">
    <template #header="{ titleId, titleClass }">
      <div class="flex-center">
        <div class="logo mr-4"></div>
        <div class="app-logo-font about-title" :id="titleId" :class="titleClass">
          {{ defaultTitle }}
        </div>
      </div>
    </template>
    <ul class="about-ui">
      <li class="flex">
        <span class="label text-right">授权数量：</span><span class="text-center">-</span>
      </li>
      <li class="flex">
        <span class="label text-right">过期时间：</span><span class="text-center">-</span>
      </li>
      <li class="flex">
        <span class="label text-right">版本：</span><span class="text-center">-</span>
      </li>
      <li class="flex">
        <span class="label text-right">版本号：</span
        ><span class="text-center">{{ PackageJSON.version }}</span>
      </li>
    </ul>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import PackageJSON from '../../../../../package.json'
const defaultTitle = import.meta.env.VITE_APP_TITLE
const aboutDialogVisible = ref(false)

const open = () => {
  aboutDialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.about-dialog {
  padding: 0;
  border-radius: 4px;
  width: 600px;
  .el-dialog__header {
    background: var(--app-header-bg-color);
    margin-right: 0;
    height: 140px;
    border-radius: 4px 4px 0 0;
    box-sizing: border-box;
  }
  .el-dialog__title {
    line-height: 140px;
  }
  .about-title {
    font-size: 40px;
  }
  .logo {
    background-image: url('@/assets/logo.png');
    background-size: 100% 100%;
    width: 59px;
    height: 59px;
  }
  .about-ui {
    padding: 24px;
    width: 360px;
    margin: 0 auto;
    line-height: 30px;
    font-weight: 400;
    .label {
      width: 180px;
      text-align: left;
      color: var(--app-text-color-secondary);
    }
  }
}
</style>
