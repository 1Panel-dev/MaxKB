<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'VoiceWaveIcon' })

const props = withDefaults(defineProps<{ size?: number | string; color?: string }>(), { size: 24 })

const waveSize = computed(() => (typeof props.size === 'number' ? `${props.size}px` : props.size))
</script>

<template>
  <span class="voice-wave-icon shrink-0" :style="{ width: waveSize, height: waveSize, color }" aria-hidden="true">
    <template v-for="barIndex in 5" :key="barIndex">
      <span class="voice-wave-icon__bar" />
    </template>
  </span>
</template>

<style scoped lang="scss">
.voice-wave-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10%;
  vertical-align: middle;

  &__bar {
    width: 10%;
    height: 40%;
    flex-shrink: 0;
    border-radius: 999px;
    background: currentColor;
    animation: voice-wave 1s ease-in-out infinite;

    &:nth-child(2),
    &:nth-child(4) {
      height: 70%;
      animation-delay: -0.2s;
    }

    &:nth-child(3) {
      height: 100%;
      animation-delay: -0.4s;
    }

    @media (prefers-reduced-motion: reduce) {
      animation: none;
    }
  }
}

@keyframes voice-wave {
  0%,
  100% {
    transform: scaleY(0.45);
  }

  50% {
    transform: scaleY(1);
  }
}
</style>
