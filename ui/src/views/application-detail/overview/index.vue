<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { copyText } from '@/utils/clipboard'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { useApplicationDetailContext } from '../context'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import HomeStatistics from '@/views/home/components/HomeStatistics.vue'
import ApplicationRanking from './components/ApplicationRanking.vue'
import ButtonEmbedThirdParty from './embed-third-party/ButtonEmbedThirdParty.vue'
import ButtonAccessRestriction from './access-restriction/ButtonAccessRestriction.vue'
import ButtonDisplaySetting from './display-setting/ButtonDisplaySetting.vue'
import ButtonApiKey from './api-key/ButtonApiKey.vue'

defineOptions({ name: 'ApplicationOverviewView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

/* 当前智能体的详情、监控与用户排行 */
const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId ?? ''))
const { application, applicationId, resourceApi } = useApplicationDetailContext()

/* 基本信息：Web 访问链接与开关 */
const accessToken = ref('')
const webAccessActive = ref(false)
const loading = ref(false)

const chatBasePath = CHAT_API_BASE_PATH.replace(/\/api$/, '')

const apiDocUrl = new URL(`${CHAT_API_BASE_PATH}-doc/`, window.location.origin).href

// TODO：分享链接还有问题
const shareUrl = computed(() => (accessToken.value ? `${window.location.origin}${chatBasePath}/${accessToken.value}` : ''))

function handleChangeWebAccess() {
  if (loading.value) return false
  loading.value = true
  return resourceApi.application
    .putAccessToken(applicationId.value, { is_active: !webAccessActive.value })
    .then((config) => {
      webAccessActive.value = config.is_active
      accessToken.value = config.access_token
      MsgSuccess(config.is_active ? '已启用' : '已禁用')
      return true
    })
    .finally(() => {
      loading.value = false
    })
}

function handleResetAccessToken() {
  if (!accessToken.value || loading.value) return
  return MsgConfirm('是否重新生成公开访问链接？', '重新生成后旧链接将失效，嵌入第三方的脚本也需要更新，请谨慎操作！', {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  }).then(
    () => {
      if (loading.value) return
      loading.value = true
      return resourceApi.application
        .putAccessToken(applicationId.value, { access_token_reset: true })
        .then((config) => {
          accessToken.value = config.access_token
          webAccessActive.value = config.is_active
          MsgSuccess('刷新成功')
        })
        .finally(() => {
          loading.value = false
        })
    },
    () => undefined,
  )
}

onMounted(() => {
  return resourceApi.application.getAccessToken(applicationId.value).then((config) => {
    accessToken.value = config.access_token
    webAccessActive.value = config.is_active
  })
})

// TODO：接入后端 API 访问开关；接入前保留禁用态。
</script>

<template>
  <!-- 基本信息 -->
  <section class="mb-4">
    <h4 class="my-4">基本信息</h4>
    <el-card shadow="never">
      <div class="flex-align-center mb-4 gap-2">
        <ApplicationIcon :icon="application?.icon" />
        <h4 class="truncate" :title="application?.name">{{ application?.name }}</h4>
      </div>
      <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div class="mk-gray-card-lg space-y-4">
          <div class="flex-between">
            <h6>Web 访问</h6>
            <!-- Web 访问开关 -->
            <el-switch :model-value="webAccessActive" size="small" :disabled="loading" :before-change="handleChangeWebAccess" />
          </div>
          <div class="space-y-2">
            <div>链接</div>
            <el-input :model-value="shareUrl" readonly>
              <template #suffix>
                <div class="-mr-1">
                  <!-- 复制访问链接 -->
                  <el-button text :disabled="!shareUrl" @click="copyText(shareUrl)">
                    <MkIcon name="icon_copy_outlined" />
                  </el-button>
                  <!-- 重置访问链接 -->
                  <el-button text :loading="loading" @click="handleResetAccessToken">
                    <MkIcon name="icon_refresh_outlined" />
                  </el-button>
                </div>
              </template>
            </el-input>
          </div>
          <div class="flex-wrap">
            <!-- 打开智能体对话；TODO：接入真实访问链接后启用跳转 -->
            <el-button plain>
              <MkIcon name="icon_new-chat_outlined" />
              <span>去对话</span>
            </el-button>
            <!-- 嵌入第三方 -->
            <ButtonEmbedThirdParty :share-url="shareUrl" :access-token="accessToken" />
            <!-- 访问限制 -->
            <ButtonAccessRestriction />
            <!-- 显示设置 -->
            <ButtonDisplaySetting />
          </div>
        </div>
        <div class="mk-gray-card-lg space-y-4">
          <div class="flex-between">
            <h6>后端 API 访问</h6>
            <!-- TODO：接入后端 API 访问开关 -->
            <el-switch size="small" disabled />
          </div>
          <div class="space-y-2">
            <div>API 文档</div>
            <el-input :model-value="apiDocUrl" readonly>
              <template #suffix>
                <!-- 复制 API 文档地址 -->
                <el-button text @click="copyText(apiDocUrl)" class="-mr-1">
                  <MkIcon name="icon_copy_outlined" />
                </el-button>
              </template>
            </el-input>
          </div>
          <!-- API Key  -->
          <ButtonApiKey />
        </div>
      </div>
    </el-card>
  </section>
  <!-- 监控 -->
  <HomeStatistics :workspace-id="workspaceId" :application-id="applicationId" :api="resourceApi.overview" />
  <!-- 排行榜 -->
  <ApplicationRanking class="mt-4" :application-id="applicationId" />
</template>
