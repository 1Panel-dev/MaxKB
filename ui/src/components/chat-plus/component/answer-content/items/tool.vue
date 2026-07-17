<template>
  <div class="tool-block mb-8">
    <div class="tool-header" @click="expanded = !expanded">
      <span class="tool-icon">🔧</span>
      <span class="tool-name">{{ content.content || '工具调用' }}</span>
      <span v-if="content.status" class="tool-status">{{ content.status }}</span>
      <span class="tool-arrow">{{ expanded ? '▲' : '▼' }}</span>
    </div>
    <div v-show="expanded" class="tool-body">
      <div v-if="content.arguments" class="tool-section">
        <div class="tool-label">参数</div>
        <pre class="tool-pre">{{ content.arguments }}</pre>
      </div>
      <div v-if="content.result" class="tool-section">
        <div class="tool-label">结果</div>
        <pre class="tool-pre">{{ content.result }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
defineProps<{ content: any }>()
const expanded = ref(false)
</script>
