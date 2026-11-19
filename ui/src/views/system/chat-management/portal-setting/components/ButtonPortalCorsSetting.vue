<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ disabled: boolean; saving?: boolean; save: (origins: string[]) => Promise<void> }>()
const allowedOrigins = defineModel<string[]>({ default: () => [] })

/* 跨域地址草稿，取消不修改已保存配置。 */
const corsVisible = ref(false)
const corsAddressDraft = ref('')

function handleOpenCorsSetting() {
  if (props.disabled || props.saving) return

  corsAddressDraft.value = allowedOrigins.value.join('\n')
  corsVisible.value = true
}

/* 按行解析跨域地址，去掉行首尾空白与空行后按顺序去重 */
function parseCorsOrigins(value: string) {
  const origins = value
    .split('\n')
    .map((origin) => origin.trim())
    .filter(Boolean)
  return [...new Set(origins)]
}

function handleSaveCorsSetting() {
  if (props.disabled || props.saving) return
  return props.save(parseCorsOrigins(corsAddressDraft.value)).then(() => {
    corsVisible.value = false
  })
}

function handleClosed() {
  corsAddressDraft.value = ''
}
</script>

<template>
  <!-- 配置跨域地址 -->
  <el-button text type="primary" :disabled="disabled || saving" @click="handleOpenCorsSetting">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="corsVisible" :title="t('portal.cors.title')" @closed="handleClosed">
    <el-input v-model="corsAddressDraft" type="textarea" :rows="8" :placeholder="t('portal.cors.placeholder')" />
    <template #footer>
      <!-- 取消跨域设置 -->
      <el-button plain :disabled="saving" @click="corsVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存跨域地址 -->
      <el-button type="primary" :loading="saving" @click="handleSaveCorsSetting">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
