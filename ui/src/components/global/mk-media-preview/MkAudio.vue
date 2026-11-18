<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { MediaPreviewProps } from './types'
import MkMediaPreview from './index.vue'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkAudio' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<MediaPreviewProps>()
defineSlots<{ default(): unknown }>()
</script>

<template>
  <MkMediaPreview v-bind="props">
    <slot />
    <template #player>
      <audio :src="src" controls tabindex="0" autoplay class="w-full max-w-160" @error="MsgWarning(t('common.messages.audioPlaybackFailed'))" />
    </template>
  </MkMediaPreview>
</template>
