<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
</script>

<template>
  <el-input v-bind="$attrs" :show-password="true" autocomplete="off" :placeholder="t('common.form.inputPlaceholder')"></el-input>
</template>
