<template>
  <LayoutContainer header="概览" back-to="-1">
    <div class="main-calc-height p-24">
      <h4 class="title-decoration-1 mb-16">应用信息</h4>
      <el-card shadow="never" class="overview-card">
        <div class="title flex align-center">
          <AppAvatar
            v-if="detail?.name"
            :name="detail?.name"
            pinyinColor
            class="mr-12"
            shape="square"
            :size="32"
          />
          <h4 class="ellipsis-1">{{ detail?.name }}</h4>
          <div class="ml-8" v-if="detail">
            <el-tag v-if="detail?.status" class="success-tag">运行中</el-tag>
            <el-tag v-else class="warning-tag">已停用</el-tag>
          </div>
        </div>
        <div class="active-button" @click.stop>
          <el-switch />
        </div>
        <el-row class="mt-16">
          <el-col :span="24">
            <el-text type="info">公开访问链接</el-text>
            <div class="mt-4">
              <span class="vertical-middle lighter">
                {{ shareUrl }}
              </span>

              <el-button type="primary" text @click="copyClick(shareUrl)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
          </el-col>
          <!-- <el-col :span="12">
            <el-text type="info">API访问凭据</el-text>
            <div class="mt-4">
              <span class="vertical-middle lighter">
                API Key: OGZmZThlZjYyYzU2MWE1OTlkYTVjZTBi
              </span>

              <el-button type="primary" text>
                   <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <div class="mt-4">
              <span class="vertical-middle lighter"> API Secret: ************** </span>
              <span>
                <el-button type="primary" text>
                     <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
              </span>
              <span>
                <el-button type="primary" text>
                  <AppIcon iconName="app-hide-password" />
                </el-button>
              </span>
            </div>
          </el-col> -->
        </el-row>
        <div class="mt-16">
          <el-button type="primary"><a :href="shareUrl" target="_blank">演示</a></el-button>
          <el-button @click="openDialog"> 嵌入第三方 </el-button>
        </div>
      </el-card>
    </div>
    <EmbedDialog ref="EmbedDialogRef"/>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import EmbedDialog from './components/EmbedDialog.vue'
import { copyClick } from '@/utils/clipboard'
import useStore from '@/stores'
const { application } = useStore()
const router = useRouter()
const route = useRoute()

const EmbedDialogRef = ref()
const shareUrl = ref('')
const accessToken = ref('')
const detail = ref<any>(null)
const apiKey = ref<any>(null)
const {
  params: { id }
} = route as any

const loading = ref(false)

function openDialog() {
  EmbedDialogRef.value.open(accessToken.value)
}
function getAccessToken() {
  application.asyncGetAccessToken(id, loading).then((res) => {
    accessToken.value = res?.data?.access_token
    shareUrl.value = application.location + res?.data?.access_token
  })
}

function getApiKey() {
  applicationApi.getAPIKey(id, loading).then((res) => {
    apiKey.value = res.data
  })
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    detail.value = res.data
  })
}
onMounted(() => {
  getDetail()
  getApiKey()
  getAccessToken()
})
</script>
<style lang="scss" scoped>
.overview-card {
  position: relative;
  .active-button {
    position: absolute;
    right: 16px;
    top: 21px;
  }
}
</style>
