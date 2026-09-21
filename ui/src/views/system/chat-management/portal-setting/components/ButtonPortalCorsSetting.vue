<script setup lang="ts">
import { ref } from 'vue'
import { MsgSuccess } from '@/utils/message'

defineProps<{ disabled?: boolean }>()
const allowedOrigins = defineModel<string[]>({ default: () => [] })

/* 跨域地址草稿，取消不修改已保存配置。 */
const corsVisible = ref(false)
const corsAddressDraft = ref('')
const corsAddressPlaceholder =
  '请输入允许的跨域地址，开启后不输入跨域地址则不限制。\n跨域地址一行一个，如：\nhttp://127.0.0.1:5678\nhttps://dataease.io'

function handleOpenCorsSetting() {
  handleClosed()
  corsAddressDraft.value = allowedOrigins.value.join('\n')
  corsVisible.value = true
}

function handleSaveCorsSetting() {
  allowedOrigins.value = corsAddressDraft.value
    .split(/\r?\n/)
    .map((address) => address.trim())
    .filter(Boolean)
  MsgSuccess('已应用到当前页面')
  corsVisible.value = false
}

function handleClosed() {
  corsAddressDraft.value = ''
}
</script>

<template>
  <!-- 配置跨域地址 -->
  <el-button text type="primary" title="跨域设置" :disabled="disabled" @click="handleOpenCorsSetting">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="corsVisible" title="跨域设置" @closed="handleClosed">
    <el-input v-model="corsAddressDraft" type="textarea" :rows="8" :placeholder="corsAddressPlaceholder" :disabled="disabled" />
    <template #footer>
      <!-- 取消跨域设置 -->
      <el-button plain @click="corsVisible = false">取消</el-button>
      <!-- 保存跨域地址 -->
      <el-button type="primary" :disabled="disabled" @click="handleSaveCorsSetting">保存</el-button>
    </template>
  </MkDialog>
</template>
