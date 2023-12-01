<template>
  <div class="chat">
    <div class="chat__header">
      <div class="chat-width">
        <h2 class="ml-24">{{ applicationDetail?.name }}</h2>
      </div>
    </div>
    <div class="chat__main chat-width" v-loading="loading">
      <AiDialog v-model:data="applicationDetail" :appId="applicationDetail?.id"></AiDialog>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AiDialog from '@/components/ai-dialog/index.vue'
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
  .chat-width {
    width: 840px;
    margin: 0 auto;
  }
}
</style>
