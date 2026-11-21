<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { MediaPreviewProps } from './types'
import MkMediaPreview from './index.vue'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkVideo' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<MediaPreviewProps>()
defineSlots<{ default(): unknown }>()
</script>

<template>
  <MkMediaPreview v-bind="props">
    <slot />
    <template #player>
      <video
        :src="src"
        controls
        tabindex="0"
        autoplay
        playsinline
        class="w-full max-h-[75vh] object-contain"
        @error="MsgWarning(t('common.error.videoPlaybackFailed'))"
      />
    </template>
  </MkMediaPreview>
</template>
