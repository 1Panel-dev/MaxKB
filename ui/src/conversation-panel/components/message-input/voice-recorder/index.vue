<script setup lang="ts">
import { computed } from 'vue'

/** 录音中面板：替换输入框显示波形、录音时长和结束按钮，录音状态由 useVoiceRecorder 维护。 */
const props = defineProps<{
  /** 已录制秒数 */
  seconds: number
  /** 各波形柱音量，0-100 */
  waveLevels: number[]
}>()

const emit = defineEmits<{
  stop: []
}>()

/** 波形在固定高度容器内围绕中线起伏。 */
const WAVE_MAX_HEIGHT = 24
const WAVE_MIN_HEIGHT = 2

const waveHeights = computed(() =>
  props.waveLevels.map((level) => WAVE_MIN_HEIGHT + (Math.max(0, Math.min(100, level)) / 100) * (WAVE_MAX_HEIGHT - WAVE_MIN_HEIGHT)),
)

const recordTime = computed(() => {
  const minutes = String(Math.floor(props.seconds / 60)).padStart(2, '0')
  const seconds = String(props.seconds % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})
</script>

<template>
  <div class="mk-input-box mk-conversation-message-input border-primary/60! bg-primary/10! w-full shadow-lg">
    <div class="flex-align-center h-8 justify-center">
      <div class="flex-align-center w-full max-w-90 justify-between px-4">
        <template v-for="(height, index) in waveHeights" :key="index">
          <span class="bg-primary w-[2px] shrink-0 rounded-full transition-[height] duration-100 ease-out" :style="{ height: `${height}px` }" />
        </template>
      </div>
    </div>
    <div class="mt-3 flex items-center justify-end">
      <span class="text-N400 mr-4">{{ recordTime }}</span>
      <!-- 结束录音并转文字 -->
      <el-button circle type="primary" @click="emit('stop')">
        <MkIcon name="icon_square_filled" />
      </el-button>
    </div>
  </div>
</template>
