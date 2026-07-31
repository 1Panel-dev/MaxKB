<script setup lang="ts">
import { computed, ref } from 'vue'
import { Grid } from '@element-plus/icons-vue'
import { qrCodeLoginMethods } from '../constants'
import type { LoginMethod, LoginMode, LoginOption, QrCodeProvider } from '../types'

defineOptions({ name: 'QrCodeLogin' })

const emit = defineEmits<{
  'change-mode': [mode: LoginMode]
}>()

const props = defineProps<{
  defaultProvider: LoginMethod
  providers: LoginOption<QrCodeProvider>[]
}>()

const isQrCodeLoginMethod = (method: LoginMethod): method is QrCodeProvider =>
  qrCodeLoginMethods.includes(method as QrCodeProvider)

const qrCodeProvider = ref<QrCodeProvider>(
  isQrCodeLoginMethod(props.defaultProvider)
    ? props.defaultProvider
    : (props.providers[0]?.value ?? 'wecom'),
)

const qrCodeProviderLabel = computed(
  () => props.providers.find((provider) => provider.value === qrCodeProvider.value)?.label ?? '',
)
</script>

<template>
  <div class="qr-login">
    <h1>扫码登录</h1>
    <div class="provider-tabs">
      <button
        v-for="provider in providers"
        :key="provider.value"
        type="button"
        :class="{ active: provider.value === qrCodeProvider }"
        @click="qrCodeProvider = provider.value"
      >
        {{ provider.label }}
      </button>
    </div>
    <div class="qr-code">
      <MkIcon :icon="Grid" :size="112" />
    </div>
    <p>请使用{{ qrCodeProviderLabel }}扫描二维码</p>
    <button type="button" class="text-action" @click="emit('change-mode', 'account')">
      返回账号登录
    </button>
  </div>
</template>

<style scoped lang="scss"></style>
