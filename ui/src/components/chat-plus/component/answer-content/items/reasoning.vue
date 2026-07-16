<template>
  <div class="reasoning">
    <button class="rc-head" @click="isExpanded = !isExpanded">
      <svg class="rc-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="rc-icon" :class="{ spin: loading }">
        <span v-if="loading" class="rc-loading"></span>
        <svg v-else viewBox="0 0 16 16" fill="none">
          <path
            d="M8 2.5C6.3 2.5 4.8 3.6 4.8 5c0 .8.3 1.5.8 2C4.7 7.5 4.2 8.4 4.2 9.3 4.2 11.3 5.8 13 8 13s3.8-1.7 3.8-3.7c0-.9-.5-1.8-1.4-2.3.5-.5.8-1.2.8-2 0-1.4-1.5-2.5-3.2-2.5Z"
            stroke="currentColor"
            stroke-width="1.2"
            stroke-linejoin="round"
          />
          <path d="M8 6.5v2.5M7 10.5h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="rc-title">{{ loading ? '思考中...' : '思考过程' }}</span>
    </button>
    <Transition
      enter-active-class="tc-expand-enter"
      leave-active-class="tc-expand-leave"
    >
      <div v-if="isExpanded" class="rc-body">
        <p v-if="content" class="rc-text">{{ content }}<span v-if="loading" class="rc-cursor">▍</span></p>
        <div v-else-if="loading" class="rc-dots"><span></span><span></span><span></span></div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{ content: any }>()

const content = computed(() => props.content.content)
const loading = computed(() => props.content.status === 'RUNNING')
const isExpanded = ref(props.content.status === 'RUNNING')

watch(() => props.content.status, (status) => {
  if (status !== 'RUNNING') {
    isExpanded.value = false
  }
})
</script>

<style scoped>
.reasoning {
  width: 100%;
}

.rc-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  color: var(--t3, #909399);
  transition: color 0.15s;
}

.rc-head:hover {
  color: var(--t1, #303133);
}

.rc-chevron {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  transition: transform 0.15s;
}

.rc-chevron.open {
  transform: rotate(90deg);
}

.rc-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--t3, #909399);
}

.rc-icon.spin {
  color: var(--t2, #606266);
}

.rc-loading {
  width: 14px;
  height: 14px;
  border: 2px solid var(--t3, #909399);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.rc-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--t2, #606266);
  white-space: nowrap;
}

.rc-body {
  padding: 6px 0 4px 8px;
}

.rc-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--t2, #606266);
  white-space: pre-wrap;
  word-break: break-word;
}

.rc-cursor {
  color: var(--t3, #909399);
  animation: blink 0.8s step-start infinite;
  font-size: 13px;
}

@keyframes blink {
  50% { opacity: 0; }
}

.rc-dots {
  display: flex;
  gap: 4px;
  padding: 4px 2px;
}

.rc-dots span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--t3, #909399);
  animation: dot-pulse 1.2s ease-in-out infinite;
}

.rc-dots span:nth-child(2) { animation-delay: 0.2s; }
.rc-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.tc-expand-enter {
  animation: tc-open 0.2s ease-out;
  overflow: hidden;
}

.tc-expand-leave {
  animation: tc-close 0.15s ease-in forwards;
  overflow: hidden;
}

@keyframes tc-open {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 600px; }
}

@keyframes tc-close {
  from { opacity: 1; max-height: 600px; }
  to { opacity: 0; max-height: 0; }
}
</style>
