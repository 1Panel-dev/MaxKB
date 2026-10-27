<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { LoginConfig, QrCodeConfig, QrCodeProvider } from '@/api/types'
import { LOGIN_METHOD } from '@/api/enums'
import { LOGIN_METHOD_LABELS } from '@/constants'
import DingTalkQrCode from '../scanComponents/dingtalkQrCode.vue'
import LarkQrCode from '../scanComponents/larkQrCode.vue'
import WecomQrCode from '../scanComponents/wecomQrCode.vue'
import type { LoginService } from '../types'

defineOptions({ name: 'QrCodeLogin' })

const props = defineProps<{ loginConfig: LoginConfig; loginService: LoginService }>()
const qrCodeLoginMethods = computed(() => props.loginConfig.login_methods ?? [])

const qrCodeConfigs = ref<Partial<Record<QrCodeProvider, QrCodeConfig>>>({})
const qrCodeProvider = ref<QrCodeProvider>((props.loginConfig.default_value as QrCodeProvider) ?? LOGIN_METHOD.WECOM)

const providerComponents = { [LOGIN_METHOD.DINGTALK]: DingTalkQrCode, [LOGIN_METHOD.LARK]: LarkQrCode, [LOGIN_METHOD.WECOM]: WecomQrCode }

const currentConfig = computed(() => qrCodeConfigs.value[qrCodeProvider.value])
const currentProviderComponent = computed(() => providerComponents[qrCodeProvider.value])

onMounted(() => {
  props.loginService.getQrCodeSources().then((sources) => {
    qrCodeConfigs.value = Object.fromEntries(sources.map(({ auth_type: provider, config }) => [provider, config]))
  })
})
</script>

<template>
  <div class="qr-login">
    <el-tabs v-model="qrCodeProvider" class="provider-tabs">
      <el-tab-pane v-for="provider in qrCodeLoginMethods" :key="provider" :label="LOGIN_METHOD_LABELS[provider]" :name="provider" />
    </el-tabs>
    <component :is="currentProviderComponent" v-if="currentConfig" :config="currentConfig" :login-service="loginService" />
  </div>
</template>

<style scoped lang="scss"></style>
