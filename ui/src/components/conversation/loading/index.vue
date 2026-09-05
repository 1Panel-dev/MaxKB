<template>
  <div class="loading-dots" :style="{ width: size + 'px', height: size + 'px' }">
    <span class="dot" />
    <span class="dot" />
    <span class="dot" />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: number
  }>(),
  {
    size: 18
  }
)
</script>

<style scoped lang="scss">
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--t3, #909399);
  animation: dot-blink 1.4s infinite both;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-blink {
  0%,
  80%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
