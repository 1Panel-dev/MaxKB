<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import ChatUserAuthScanApi from '@/api/admin/system/chat-user/chat-user-auth-scan'
import type { QrCodeProvider, QrLoginPlatform, QrLoginPlatformPayload } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS, SCAN_FIELD_LABELS } from '@/constants'
import { MsgSuccess, MsgError } from '@/utils/message'
import dingtalkLogo from '@/assets/logo/logo_dingtalk.svg'
import enterpriseWechatLogo from '@/assets/logo/logo_enterprise-wechat.svg'
import larkLogo from '@/assets/logo/logo_lark.svg'
import EditSCANDrawer from '../EditSCANDrawer.vue'

interface QrLoginPlatformView extends QrLoginPlatformPayload {
  isValid: boolean
  logo: string
}

const platformDefinitions: {
  configKeys: string[]
  key: QrCodeProvider
  logo: string
}[] = [
  {
    key: LOGIN_METHOD.WECOM,
    logo: enterpriseWechatLogo,
    configKeys: ['corp_id', 'agent_id', 'app_secret'],
  },
  {
    key: LOGIN_METHOD.DINGTALK,
    logo: dingtalkLogo,
    configKeys: ['corp_id', 'app_key', 'app_secret'],
  },
  { key: LOGIN_METHOD.LARK, logo: larkLogo, configKeys: ['app_key', 'app_secret'] },
]

const apiBaseUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api`

const loading = ref(false)
const qrLoginPlatforms = ref<QrLoginPlatformView[]>([])

function createQrLoginPlatforms(settings: QrLoginPlatform[]): QrLoginPlatformView[] {
  return platformDefinitions.map(({ configKeys, key, logo }) => {
    const setting = settings.find(({ auth_type }) => auth_type === key)

    return {
      key,
      logo,
      config: Object.fromEntries([
        ...configKeys.map((configKey) => [configKey, setting?.config[configKey] ?? '']),
        ['callback_url', setting?.config.callback_url || `${apiBaseUrl}/${key}`],
      ]),
      isActive: setting?.is_active ?? false,
      isValid: setting?.is_valid ?? false,
    }
  })
}

/* 扫码登录平台加载与状态切换 */
function loadQrPlatforms() {
  loading.value = true
  return ChatUserAuthScanApi.getQrLoginPlatforms()
    .then((settings) => {
      qrLoginPlatforms.value = createQrLoginPlatforms(settings)
    })
    .finally(() => {
      loading.value = false
    })
}

/* 改变状态 */
function handlePlatformStatusChange(platform: QrLoginPlatformView) {
  loading.value = true
  return ChatUserAuthScanApi.postQrLoginPlatform({
    key: platform.key,
    config: platform.config,
    isActive: platform.isActive,
  })
    .then(() => MsgSuccess('保存成功'))
    .catch((error) => {
      platform.isActive = !platform.isActive
      throw error
    })
    .finally(() => {
      loading.value = false
    })
}

/* 编辑 */
const editScanDrawerRef = useTemplateRef<InstanceType<typeof EditSCANDrawer>>('editScanDrawerRef')

function handleEditPlatform(platform: QrLoginPlatformView) {
  editScanDrawerRef.value?.open(platform)
}

/* 校验 */
function handleValidatePlatform(platform: QrLoginPlatformView) {
  loading.value = true
  return ChatUserAuthScanApi.putValidateQrLoginPlatform(platform)
    .then((res) => {
      res ? MsgSuccess('校验成功') : MsgError('校验失败')
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(loadQrPlatforms)
</script>

<template>
  <div class="pr-2 flex flex-col gap-4">
    <template v-for="platform in qrLoginPlatforms" :key="platform.key">
      <el-card shadow="hover">
        <div class="flex-between mb-4">
          <div class="flex items-center gap-2">
            <img :src="platform.logo" :alt="LOGIN_METHOD_LABELS[platform.key]" class="h-6 w-6" />
            <h4>{{ LOGIN_METHOD_LABELS[platform.key] }}</h4>
            <el-tag v-if="platform.isValid" size="small" type="success">有效</el-tag>
            <!-- <el-tag v-if="!platform.isValid" size="small" type="danger">无效</el-tag> -->
          </div>

          <div v-if="platform.isValid" class="flex items-center gap-2">
            <span>{{ platform.isActive ? '已启用' : '已关闭' }}</span>
            <el-switch v-model="platform.isActive" @change="handlePlatformStatusChange(platform)" />
          </div>
          <el-button  v-else type="primary" @click="handleEditPlatform(platform)">接入</el-button>
        </div>
        <div class="border-t" v-if="platform.isValid">
          <div class="py-4 grid grid-cols-2 gap-x-6 gap-y-4">
            <div v-for="(value, key) in platform.config" :key="key">
              <p class="text-N600">{{ SCAN_FIELD_LABELS[key] ?? key }}</p>
              <p>
                {{ key === 'app_secret' ? '••••••••••••' : value }}
              </p>
            </div>
          </div>

          <el-button type="primary" @click="handleEditPlatform(platform)">编辑</el-button>
          <el-button plain @click="handleValidatePlatform(platform)">校验</el-button>
        </div>
      </el-card>
    </template>
  </div>

  <EditSCANDrawer ref="editScanDrawerRef" @refresh="loadQrPlatforms" />
</template>
