<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { copyText } from '@/utils/clipboard'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import type { ApiInputField } from '@/workflow-canvas/nodes/base-node/types'
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
const webAccessActive = ref<boolean>()
const savingWebAccess = ref(false)
const resettingAccessToken = ref(false)
const chatBasePath = CHAT_API_BASE_PATH.replace(/\/api$/, '')
const apiDocUrl = new URL(`${CHAT_API_BASE_PATH}-doc/`, window.location.origin).href

const shareUrl = computed(() => {
  if (!accessToken.value) return ''
  const url = new URL(`${chatBasePath}/${accessToken.value}`, window.location.origin)
  const baseProperties = application.value?.work_flow?.nodes?.find((node) => node.id === 'base-node')?.properties as
    | { api_input_field_list?: ApiInputField[]; input_field_list?: ApiInputField[] }
    | undefined
  const inputFields =
    baseProperties?.api_input_field_list ?? baseProperties?.input_field_list?.filter((field) => field.assignment_method === 'api_input') ?? []
  // 沿用 V2 访问链接的参数编码方式，兼容旧版工作流输入配置。
  inputFields.forEach((field) => {
    url.searchParams.append(encodeURIComponent(field.variable), encodeURIComponent(field.default_value ?? ''))
  })
  return url.href
})

function handleChangeWebAccess() {
  if (webAccessActive.value === undefined || savingWebAccess.value || resettingAccessToken.value) return false
  savingWebAccess.value = true
  return resourceApi.application
    .putAccessToken(applicationId.value, { is_active: !webAccessActive.value })
    .then((config) => {
      webAccessActive.value = config.is_active
      accessToken.value = config.access_token
      MsgSuccess(config.is_active ? '已启用' : '已禁用')
      return true
    })
    .finally(() => {
      savingWebAccess.value = false
    })
}

function handleResetAccessToken() {
  if (!accessToken.value || resettingAccessToken.value || savingWebAccess.value) return
  return MsgConfirm('是否重新生成公开访问链接？', '重新生成后旧链接将失效，嵌入第三方的脚本也需要更新，请谨慎操作！', {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  }).then(
    () => {
      if (resettingAccessToken.value || savingWebAccess.value) return
      resettingAccessToken.value = true
      return resourceApi.application
        .putAccessToken(applicationId.value, { access_token_reset: true })
        .then((config) => {
          accessToken.value = config.access_token
          webAccessActive.value = config.is_active
          MsgSuccess('刷新成功')
        })
        .finally(() => {
          resettingAccessToken.value = false
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
            <el-switch
              :model-value="webAccessActive ?? false"
              size="small"
              :disabled="webAccessActive === undefined || savingWebAccess || resettingAccessToken"
              :before-change="handleChangeWebAccess"
            />
          </div>
          <div class="space-y-2">
            <div>链接</div>
            <el-input :model-value="shareUrl" readonly placeholder="暂无访问链接">
              <template #suffix>
                <span class="flex-align-center gap-3">
                  <!-- 复制访问链接 -->
                  <el-button link :disabled="!shareUrl" @click="copyText(shareUrl)">
                    <MkIcon name="icon_copy_outlined" />
                  </el-button>
                  <!-- 重置访问链接 -->
                  <el-button link :disabled="!shareUrl || savingWebAccess" :loading="resettingAccessToken" @click="handleResetAccessToken">
                    <MkIcon name="icon_refresh_outlined" />
                  </el-button>
                </span>
              </template>
            </el-input>
          </div>
          <div class="flex-wrap">
            <!-- 打开智能体对话；TODO：接入真实访问链接后启用跳转 -->
            <el-button plain>
              <MkIcon name="icon_new-chat_outlined" />
              <span>去对话</span>
            </el-button>
            <ButtonEmbedThirdParty :share-url="shareUrl" :access-token="accessToken" />
            <ButtonAccessRestriction />
            <ButtonDisplaySetting />
          </div>
        </div>
        <div class="mk-gray-card-lg space-y-4">
          <div class="flex-between">
            <h6>后端 API 访问</h6>
            <!-- 后端 API 访问开关 -->
            <MkTooltip content="访问配置待接入">
              <span class="flex-align-center"><el-switch size="small" disabled /></span>
            </MkTooltip>
          </div>
          <div class="space-y-2">
            <div>API 文档</div>
            <el-input :model-value="apiDocUrl" readonly>
              <template #suffix>
                <!-- 复制 API 文档地址 -->
                <el-button link @click="copyText(apiDocUrl)">
                  <MkIcon name="icon_copy_outlined" />
                </el-button>
              </template>
            </el-input>
          </div>
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
