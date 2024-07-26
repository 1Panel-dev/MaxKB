<template>
  <div class="chat layout-bg" v-loading="loading">
    <div class="chat__header" :class="!isDefaultTheme ? 'custom-header' : ''">
      <div class="chat-width flex align-center">
        <div class="mr-12 ml-24 flex">
          <AppAvatar
            v-if="isAppIcon(applicationDetail?.icon)"
            shape="square"
            :size="32"
            style="background: none"
          >
            <img :src="applicationDetail?.icon" alt="" />
          </AppAvatar>
          <AppAvatar
            v-else-if="applicationDetail?.name"
            :name="applicationDetail?.name"
            pinyinColor
            shape="square"
            :size="32"
          />
        </div>

        <h2>{{ applicationDetail?.name }}</h2>
      </div>
    </div>
    <div class="chat__main chat-width">
      <AiChat
        v-model:data="applicationDetail"
        :available="applicationAvailable"
        :appId="applicationDetail?.id"
      ></AiChat>
    </div>
    <div class="chat__footer"></div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
const route = useRoute()
const {
  params: { accessToken }
} = route as any

const { application, user } = useStore()

const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})

const loading = ref(false)
const applicationDetail = ref<any>({})
const applicationAvailable = ref<boolean>(true)

function getAccessToken(token: string) {
  application
    .asyncAppAuthentication(token, loading)
    .then(() => {
      getAppProfile()
    })
    .catch(() => {
      applicationAvailable.value = false
    })
}
function getAppProfile() {
  application
    .asyncGetAppProfile(loading)
    .then((res: any) => {
      applicationDetail.value = res.data
    })
    .catch(() => {
      applicationAvailable.value = false
    })
}

onMounted(() => {
  user.changeUserType(2)
  getAccessToken(accessToken)
})
</script>
<style lang="scss">
.chat {
  overflow: hidden;
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
    border-bottom: 1px solid var(--el-border-color);
  }
  &__main {
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 24px);
    overflow: hidden;
  }

  &__footer {
    background: #f3f7f9;
    height: 80px;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    box-sizing: border-box;
    border-radius: 8px !important;
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
    max-width: var(--app-chat-width, 860px);
    margin: 0 auto;
  }
}
</style>
