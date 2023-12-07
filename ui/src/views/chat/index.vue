<template>
  <div class="chat" v-loading="loading">
    <div class="chat__header">
      <div class="chat-width">
        <h2 class="ml-24">{{ applicationDetail?.name }}</h2>
      </div>
    </div>
    <div class="chat__main chat-width">
      <AiChat v-model:data="applicationDetail" :appId="applicationDetail?.id"></AiChat>
    </div>
    <div class="chat__footer"></div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import useStore from '@/stores'
const route = useRoute()
const {
  params: { accessToken }
} = route as any

const { application, user } = useStore()

const loading = ref(false)
const applicationDetail = ref<any>({})

function getAccessToken(token: string) {
  application.asyncAppAuthentication(token, loading).then((res) => {
    getProfile()
  })
}
function getProfile() {
  applicationApi.getProfile(loading).then((res) => {
    applicationDetail.value = res.data
  })
}
onMounted(() => {
  user.changeUserType(2)
  getAccessToken(accessToken)
})
</script>
<style lang="scss" scoped>
.chat {
  background-color: var(--app-layout-bg-color);
  &__header {
    background: var(--app-header-bg-color);
    position: fixed;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    padding: var(--app-header-padding);
  }
  &__main {
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 24px);
  }
  &__footer {
    background: #f3f7f9;
    height: 80px;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    box-sizing: border-box;
    &:before {
      background: linear-gradient(0deg, #f3f7f9 0%, rgba(243, 247, 249, 0) 100%);
      content: '';
      position: absolute;
      width: 100%;
      top: -16px;
      left: 0;
      height: 16px;
    }
  }
  .chat-width {
    width: 860px;
    margin: 0 auto;
  }
}
</style>
