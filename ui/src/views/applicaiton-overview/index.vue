<template>
  <LayoutContainer header="概览">
    <div class="main-calc-height p-24" style="min-width: 600px">
      <h4 class="title-decoration-1 mb-16">应用信息</h4>
      <el-card shadow="never" class="overview-card" v-loading="loading">
        <div class="title flex align-center">
          <AppAvatar
            v-if="detail?.name"
            :name="detail?.name"
            pinyinColor
            class="mr-12"
            shape="square"
            :size="32"
          />
          <h4>{{ detail?.name }}</h4>
        </div>

        <el-row :gutter="12">
          <el-col :span="12" class="mt-16">
            <div class="flex">
              <el-text type="info">公开访问链接</el-text>
              <el-switch
                v-model="accessToken.is_active"
                class="ml-8"
                size="small"
                inline-prompt
                active-text="开"
                inactive-text="关"
                @change="changeState($event)"
              />
            </div>

            <div class="mt-4 mb-16 url-height">
              <span class="vertical-middle lighter break-all">
                {{ shareUrl }}
              </span>

              <el-button type="primary" text @click="copyClick(shareUrl)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
              <el-button @click="refreshAccessToken" type="primary" text style="margin-left: 1px">
                <el-icon><RefreshRight /></el-icon>
              </el-button>
            </div>
            <div>
              <el-button :disabled="!accessToken?.is_active" type="primary">
                <a v-if="accessToken?.is_active" :href="shareUrl" target="_blank"> 演示 </a>
                <span v-else>演示</span>
              </el-button>
              <el-button :disabled="!accessToken?.is_active" @click="openDialog">
                嵌入第三方
              </el-button>
            </div>
          </el-col>
          <el-col :span="12" class="mt-16">
            <div class="flex">
              <el-text type="info">API访问凭据</el-text>
            </div>
            <div class="mt-4 mb-16 url-height">
              <span class="vertical-middle lighter break-all">
                {{ apiUrl }}
              </span>

              <el-button type="primary" text @click="copyClick(apiUrl)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <div>
              <el-button @click="openAPIKeyDialog"> API Key </el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
    <EmbedDialog ref="EmbedDialogRef" />
    <APIKeyDialog ref="APIKeyDialogRef" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import EmbedDialog from './component/EmbedDialog.vue'
import APIKeyDialog from './component/APIKeyDialog.vue'
import applicationApi from '@/api/application'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { copyClick } from '@/utils/clipboard'
import useStore from '@/stores'
const { application } = useStore()
const router = useRouter()
const route = useRoute()
const {
  params: { id }
} = route as any

const apiUrl = window.location.origin + '/doc'

const APIKeyDialogRef = ref()
const EmbedDialogRef = ref()

const accessToken = ref<any>({})
const detail = ref<any>(null)

const loading = ref(false)

const shareUrl = computed(() => application.location + accessToken.value.access_token)

function refreshAccessToken() {
  const obj = {
    access_token_reset: true
  }
  const str = '刷新成功'
  updateAccessToken(obj, str)
}
function changeState(bool: Boolean) {
  const obj = {
    is_active: bool
  }
  const str = bool ? '启用成功' : '禁用成功'
  updateAccessToken(obj, str)
}

function updateAccessToken(obj: any, str: string) {
  applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
    accessToken.value = res?.data
    MsgSuccess(str)
  })
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}
function openDialog() {
  EmbedDialogRef.value.open(accessToken.value?.access_token)
}
function getAccessToken() {
  application.asyncGetAccessToken(id, loading).then((res: any) => {
    accessToken.value = res?.data
  })
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    detail.value = res.data
  })
}
onMounted(() => {
  getDetail()
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
  .url-height {
    // min-height: 50px;
  }
}
</style>
