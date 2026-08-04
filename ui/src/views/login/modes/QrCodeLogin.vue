<script setup lang="ts">
import { ref } from 'vue'
import { qrCodeLoginMethods } from '../constants'
import type { LoginMethod, LoginOption, QrCodeProvider } from '../types'

defineOptions({ name: 'QrCodeLogin' })

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
</script>

<template>
  <div class="qr-login">
    <el-tabs v-model="qrCodeProvider" class="provider-tabs">
      <el-tab-pane
        v-for="provider in providers"
        :key="provider.value"
        :label="provider.label"
        :name="provider.value"
      />
    </el-tabs>
    <div class="qr-code"></div>
  </div>
</template>

<style scoped lang="scss"></style>
