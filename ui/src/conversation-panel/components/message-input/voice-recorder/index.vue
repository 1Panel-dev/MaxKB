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

/** 波形柱最大高度（px），与波形容器 h-8 一致。 */
const WAVE_MAX_HEIGHT = 32

const recordTime = computed(() => {
  const minutes = String(Math.floor(props.seconds / 60)).padStart(2, '0')
  const seconds = String(props.seconds % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})
</script>

<template>
  <div class="mk-input-box mk-conversation-message-input border-primary! bg-primary/[0.06] w-full shadow-lg">
    <div class="flex h-8 items-center justify-center gap-0.5">
      <span
        v-for="(level, index) in waveLevels"
        :key="index"
        class="bg-primary w-0.5 rounded-full transition-[height] duration-100"
        :style="{ height: `${Math.max(2, (level / 100) * WAVE_MAX_HEIGHT)}px` }"
      />
    </div>
    <div class="mt-3 flex items-center justify-end">
      <span class="text-N600 mr-3 text-xs">{{ recordTime }}</span>
      <!-- 结束录音并转文字 -->
      <el-button circle type="primary" @click="emit('stop')">
        <MkIcon name="icon_square_filled" />
      </el-button>
    </div>
  </div>
</template>
