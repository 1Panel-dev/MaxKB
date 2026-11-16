<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n({ useScope: 'global' })
</script>

<template>
  <el-input v-bind="$attrs" type="textarea" :placeholder="t('common.placeholders.input')"></el-input>
</template>
