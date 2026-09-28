<script setup lang="ts">
import MkMediaPreview from './index.vue'
import { MsgWarning } from '@/utils/message'
import type { MediaPreviewProps } from './types'

defineOptions({ name: 'MkVideo' })
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
        @error="MsgWarning('无法播放，请检查视频格式或文件地址')"
      />
    </template>
  </MkMediaPreview>
</template>
