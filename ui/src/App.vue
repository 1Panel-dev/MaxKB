<script setup lang="ts">
import { computed } from 'vue'
import 'dayjs/locale/zh-cn'
import 'dayjs/locale/zh-tw'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import { normalizeLocale } from '@/locales/config'
import { RouterView } from 'vue-router'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'

const { locale } = useI18n({ useScope: 'global' })
const elementLocales = { 'zh-CN': zhCn, 'en-US': en, 'zh-Hant': zhTw }
const elementLocale = computed(() => elementLocales[normalizeLocale(locale.value)])

const tableConfig = { tooltipOptions: { showAfter: TOOLTIP_SHOW_DELAY } }
</script>

<template>
  <el-config-provider :table="tableConfig" :locale="elementLocale">
    <RouterView />
  </el-config-provider>
</template>
