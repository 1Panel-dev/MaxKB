<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })
</script>

<template>
  <div class="flex-center mt-24">
    <div>
      <img src="@/assets/error/500.png" width="250" alt="" />
      <h4 class="text-center">{{ t('common.error.noPermission') }}</h4>
    </div>
  </div>
</template>
