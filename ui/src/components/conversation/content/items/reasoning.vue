<template>
  <div class="reasoning">
    <button class="rc-head" @click="isExpanded = !isExpanded">
      <svg class="rc-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="rc-title">思考过程</span>
    </button>
    <div v-show="isExpanded" class="rc-body">
      <pre class="rc-text">{{ content.content }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ content: any }>()
const isExpanded = ref(true)
let prevStatus = props.content.status

watch(() => props.content.status, (status) => {
  if (prevStatus === 'RUNNING' && status !== 'RUNNING') {
    isExpanded.value = false
  }
  prevStatus = status
})
</script>

<style scoped>
.reasoning {
  width: 100%;
  margin-bottom: 8px;
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

.rc-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--t2, #606266);
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
  font-family: inherit;
}
</style>
