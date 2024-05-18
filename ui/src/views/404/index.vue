<template>
  <el-row class="not-found-container">
    <el-col class="img" :xs="0" :sm="0" :md="12" :lg="12" :xl="12"> </el-col>
    <el-col class="message-container" :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
      <div class="title">{{ $t('views.notFound.title')}}</div>
      <div class="message">{{ $t('views.notFound.message') }}</div>
      <!-- TODO 暂时不处理 -->
      <!-- <div class="operate"><el-button type="primary" @click="router.push('/')">{{ $t('views.notFound.operate') }}</el-button></div> -->
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<style lang="scss" scoped>
.not-found-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;

  .img {
    background-image: url('@/assets/404.png');
    background-size: 100% 100%;
    width: 50%;
    height: 100%;
  }

  .message-container {
    color: var(--app-text-color);

    .title {
      font-size: 50px;
      font-weight: 500;
    }

    .message {
      font-size: 20px;
      margin: 30px 0 20px 0;
    }
  }
}

@media only screen and (max-width: 1000px) {
  .not-found-container .message-container {
    text-align: center;
  }
}
</style>
