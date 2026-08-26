<script setup lang="ts">
import animationBottom from '@/assets/login-animation/1bottom.png'
import animationCircle from '@/assets/login-animation/2circle.png'
import animationLine from '@/assets/login-animation/3line.gif'
import animationRobot from '@/assets/login-animation/4robot.gif'
import animationPanel from '@/assets/login-animation/5panel.png'

defineOptions({ name: 'DefaultThemeAnimation' })
</script>

<template>
  <div class="default-theme-animation w-full" aria-hidden="true">
    <img :src="animationBottom" alt="" class="animation-bottom" />
    <img :src="animationCircle" alt="" class="animation-circle" />
    <img :src="animationLine" alt="" class="animation-line" />
    <img :src="animationPanel" alt="" class="animation-panel" />
    <img :src="animationRobot" alt="" class="animation-robot" />
  </div>
</template>

<style scoped lang="scss">
.default-theme-animation {
  aspect-ratio: 720 / 580;
  position: relative;
}

.animation-bottom,
.animation-circle,
.animation-line,
.animation-panel,
.animation-robot {
  height: auto;
  max-width: none;
  pointer-events: none;
  position: absolute;
  user-select: none;
}

.animation-bottom {
  left: 13.61%;
  top: 49.21%;
  width: 78.78%;
}

.animation-circle {
  animation: animation-circle-float 3s ease-in-out infinite;
  left: 0;
  top: 40.09%;
  width: 100%;
}

.animation-line {
  left: 12.92%;
  top: 0;
  width: 68.4%;
}

.animation-panel {
  left: 58%;
  top: 14.54%;
  width: 26.68%;
}

.animation-robot {
  left: 32.22%;
  top: 36.31%;
  width: 25.95%;
}

@keyframes animation-circle-float {
  0%,
  100% {
    transform: translateY(-6px);
  }

  50% {
    transform: translateY(6px);
  }
}
</style>
