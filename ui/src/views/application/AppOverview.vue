<template>
  <LayoutContainer header="概览" back-to="-1">
    <div class="main-calc-height p-24">
      <h4 class="title-decoration-1 mb-16">应用信息</h4>
      <el-card shadow="never" class="overview-card">
        <div class="title flex align-center">
          <AppAvatar class="mr-12" shape="square" :size="32">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
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

              <el-button type="primary" text>
                <el-icon style="font-size: 13px"><CopyDocument /></el-icon>
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
                <el-icon style="font-size: 13px"><CopyDocument /></el-icon>
              </el-button>
            </div>
            <div class="mt-4">
              <span class="vertical-middle lighter"> API Secret: ************** </span>
              <span>
                <el-button type="primary" text>
                  <el-icon style="font-size: 13px"><CopyDocument /></el-icon>
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
          <el-button type="primary"> 演示 </el-button>
          <el-button @click="openDialog"> 嵌入第三方 </el-button>
        </div>
      </el-card>
    </div>
    <EmbedDialog ref="EmbedDialogRef" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import EmbedDialog from './components/EmbedDialog.vue'
import useStore from '@/stores'
const { application } = useStore()
const router = useRouter()
const route = useRoute()

const EmbedDialogRef = ref()
const shareUrl = ref('')
const detail = ref<any>(null)
const apiKey = ref<any>(null)
const {
  params: { id }
} = route as any

const loading = ref(false)

function openDialog() {
  EmbedDialogRef.value.open()
}
function getAccessToken() {
  application.asyncGetAccessToken(id, loading).then((res) => {
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
