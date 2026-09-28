<script setup lang="ts">
import MkMediaPreview from './index.vue'
import { MsgWarning } from '@/utils/message'
import type { MediaPreviewProps } from './types'

defineOptions({ name: 'MkAudio' })
const props = defineProps<MediaPreviewProps>()
defineSlots<{ default(): unknown }>()
</script>

<template>
  <MkMediaPreview v-bind="props">
    <slot />
    <template #player>
      <audio :src="src" controls tabindex="0" autoplay class="w-full max-w-160" @error="MsgWarning('无法播放，请检查音频格式或文件地址')" />
    </template>
  </MkMediaPreview>
</template>
