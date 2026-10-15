<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import AuthScanApi from '@/api/admin/system/settings/auth-scan-setting'
import type { QrCodeProvider, QrLoginPlatform, QrLoginPlatformPayload } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import { MsgSuccess } from '@/utils/message'
import dingtalkLogo from '@/assets/logo/logo_dingtalk.svg'
import enterpriseWechatLogo from '@/assets/logo/logo_enterprise-wechat.svg'
import larkLogo from '@/assets/logo/logo_lark.svg'
import EditSCANDrawer from '../EditSCANDrawer.vue'

interface QrLoginPlatformView extends QrLoginPlatformPayload {
  isValid: boolean
  logo: string
}

const platformDefinitions: { configKeys: string[]; key: QrCodeProvider; logo: string }[] = [
  { key: LOGIN_METHOD.WECOM, logo: enterpriseWechatLogo, configKeys: ['corp_id', 'agent_id', 'app_secret'] },
  { key: LOGIN_METHOD.DINGTALK, logo: dingtalkLogo, configKeys: ['corp_id', 'app_key', 'app_secret'] },
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
  return AuthScanApi.getQrLoginPlatforms()
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
  return AuthScanApi.putQrLoginPlatform({ key: platform.key, config: platform.config, isActive: platform.isActive })
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

onMounted(loadQrPlatforms)
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <template v-for="platform in qrLoginPlatforms" :key="platform.key">
      <!-- 点击平台卡片配置扫码登录 -->
      <el-card shadow="hover" @click="handleEditPlatform(platform)">
        <div class="flex-between">
          <div class="flex-align-center gap-2">
            <img :src="platform.logo" :alt="LOGIN_METHOD_LABELS[platform.key]" class="h-6 w-6" />
            <h4>{{ LOGIN_METHOD_LABELS[platform.key] }}</h4>
            <el-tag v-if="platform.isValid" size="small" type="success">有效</el-tag>
          </div>

          <div class="flex-align-center gap-4">
            <!-- 配置扫码登录平台 -->
            <el-button plain @click.stop="handleEditPlatform(platform)">{{ platform.isValid ? '配置' : '未配置' }}</el-button>
            <template v-if="platform.isValid">
              <el-divider direction="vertical" />
              <!-- 启停扫码登录，阻止点击打开配置 -->
              <span class="inline-flex" @click.stop>
                <el-switch v-model="platform.isActive" @change="handlePlatformStatusChange(platform)" />
              </span>
            </template>
          </div>
        </div>
      </el-card>
    </template>
  </div>

  <EditSCANDrawer ref="editScanDrawerRef" @refresh="loadQrPlatforms" />
</template>
