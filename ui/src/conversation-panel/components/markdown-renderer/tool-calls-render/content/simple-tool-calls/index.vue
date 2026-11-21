<template>
  <div>
    <p class="my-2">{{ t('execution.details.inputParams') }}：</p>
    <span class="text-N500">{{ content.content.input }}</span>
    <p class="my-2">{{ t('execution.details.outputParams') }}：</p>
    <span class="text-N500">
      <pre>{{ content.content.output }}</pre>
    </span>
  </div>
</template>
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { type ToolCalls } from '../../index'

const { t } = useI18n({ useScope: 'global' })
defineProps<{
  content: ToolCalls
}>()
</script>
<style lang="scss" scoped></style>
