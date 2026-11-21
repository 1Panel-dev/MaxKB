<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineOptions({ name: 'ConversationFailureContent' })

const { t } = useI18n({ useScope: 'global' })
defineProps<{
  content: { content?: string | null }
}>()
</script>

<template>
  <div class="flex-align-center gap-2">
    <MkIcon name="icon_warning_filled" class="text-danger!" />
    <span class="text-[16px]">{{ content.content || t('chat.message.errorOccurred') }}</span>
  </div>
</template>

<style scoped lang="scss"></style>
