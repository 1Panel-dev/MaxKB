<template>
  <div ref="scrollRef" class="tc-scroll">
    <FileDiff :file="file" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import FileDiff from '../patch/FileDiff.vue'
import type { PatchFileInfo } from '../patch/patchTypes'
import { Scroll } from '@/conversation-panel/core/stream'

const props = defineProps<{ file: PatchFileInfo }>()

const scrollRef = ref<HTMLElement>()
let scroll: Scroll | null = null

onMounted(() => {
  if (scrollRef.value) {
    scroll = new Scroll(scrollRef.value)
    scroll.forceBottom()
  }
})

watch(
  () => props.file.additions,
  () => {
    nextTick(() => scroll?.scrollBottom())
  },
)
</script>

<style scoped>
.tc-scroll {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 6px;
  border: 1px solid var(--mk-N300);
}
</style>
