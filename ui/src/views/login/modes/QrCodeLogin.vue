<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import externalLoginApi from '@/api/admin/auth/external-login'
import type { LoginConfig, QrCodeConfig } from '@/api/admin/auth/types'
import { loginMethodLabels, qrCodeLoginMethods } from '../constants'
import DingTalkQrCode from '../scanComponents/dingtalkQrCode.vue'
import LarkQrCode from '../scanComponents/larkQrCode.vue'
import WecomQrCode from '../scanComponents/wecomQrCode.vue'
import type { QrCodeProvider } from '../types'

defineOptions({ name: 'QrCodeLogin' })

const props = defineProps<{ loginConfig: LoginConfig }>()
const qrCodeProviders = computed(() =>
  (props.loginConfig.login_methods ?? [])
    .filter((method): method is QrCodeProvider =>
      qrCodeLoginMethods.some((provider) => provider === method),
    )
    .map((method) => ({ label: loginMethodLabels[method], value: method })),
)
const qrCodeConfigs = ref<Partial<Record<QrCodeProvider, QrCodeConfig>>>({})
const defaultProvider = props.loginConfig.default_value
const qrCodeProvider = ref<QrCodeProvider>(
  qrCodeLoginMethods.some((provider) => provider === defaultProvider)
    ? (defaultProvider as QrCodeProvider)
    : (qrCodeProviders.value[0]?.value ?? 'wecom'),
)

const providerComponents = {
  dingtalk: DingTalkQrCode,
  lark: LarkQrCode,
  wecom: WecomQrCode,
}

const currentConfig = computed(() => qrCodeConfigs.value[qrCodeProvider.value])
const currentProviderComponent = computed(() => providerComponents[qrCodeProvider.value])

onMounted(async () => {
  const sources = await externalLoginApi.getQrCodeSources()
  qrCodeConfigs.value = Object.fromEntries(
    sources.map(({ auth_type: provider, config }) => [provider, config]),
  )
})
</script>

<template>
  <div class="qr-login">
    <el-tabs v-model="qrCodeProvider" class="provider-tabs">
      <el-tab-pane
        v-for="provider in qrCodeProviders"
        :key="provider.value"
        :label="provider.label"
        :name="provider.value"
      />
    </el-tabs>
    <component :is="currentProviderComponent" v-if="currentConfig" :config="currentConfig" />
  </div>
</template>

<style scoped lang="scss"></style>
