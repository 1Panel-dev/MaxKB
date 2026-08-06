<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import ExternalLoginApi from '@/api/admin/auth/external-login'
import { LOGIN_METHOD_LABELS } from '@/constants/auth.ts'
import type { LoginConfig, QrCodeConfig, QrCodeProvider } from '@/types'
import DingTalkQrCode from '../scanComponents/dingtalkQrCode.vue'
import LarkQrCode from '../scanComponents/larkQrCode.vue'
import WecomQrCode from '../scanComponents/wecomQrCode.vue'

defineOptions({ name: 'QrCodeLogin' })

const props = defineProps<{ loginConfig: LoginConfig }>()
const qrCodeLoginMethods = computed(() => props.loginConfig.login_methods ?? [])

const qrCodeConfigs = ref<Partial<Record<QrCodeProvider, QrCodeConfig>>>({})
const qrCodeProvider = ref<QrCodeProvider>(
  (props.loginConfig.default_value as QrCodeProvider) ?? 'wecom',
)

const providerComponents = {
  dingtalk: DingTalkQrCode,
  lark: LarkQrCode,
  wecom: WecomQrCode,
}

const currentConfig = computed(() => qrCodeConfigs.value[qrCodeProvider.value])
const currentProviderComponent = computed(() => providerComponents[qrCodeProvider.value])

onMounted(() => {
  ExternalLoginApi.getQrCodeSources().then((sources) => {
    qrCodeConfigs.value = Object.fromEntries(
      sources.map(({ auth_type: provider, config }) => [provider, config]),
    )
  })
})
</script>

<template>
  <div class="qr-login">
    <el-tabs v-model="qrCodeProvider" class="provider-tabs">
      <el-tab-pane
        v-for="provider in qrCodeLoginMethods"
        :key="provider"
        :label="LOGIN_METHOD_LABELS[provider]"
        :name="provider"
      />
    </el-tabs>
    <component :is="currentProviderComponent" v-if="currentConfig" :config="currentConfig" />
  </div>
</template>

<style scoped lang="scss"></style>
