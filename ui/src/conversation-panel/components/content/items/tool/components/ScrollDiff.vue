<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Scroll } from '@/conversation-panel/core/scroll'
import FileDiff from '../patch/FileDiff.vue'
import type { PatchFileInfo } from '../patch/patchTypes'

defineOptions({ name: 'ConversationScrollDiff' })

const props = defineProps<{ file: PatchFileInfo }>()

// 初始化差异滚动容器，并在卸载时释放监听和动画帧。
const diffScrollRef = ref<HTMLElement>()
let diffScroll: Scroll | null = null

onMounted(() => {
  if (!diffScrollRef.value) return
  diffScroll = new Scroll(diffScrollRef.value)
  diffScroll.forceBottom()
})

onBeforeUnmount(() => diffScroll?.destroy())

// 新增代码渲染后，仅在用户仍位于底部时跟随滚动。
watch(
  () => props.file.additions,
  () => diffScroll?.scrollBottom(),
  { flush: 'post' },
)
</script>

<template>
  <div ref="diffScrollRef" class="max-h-[400px] overflow-y-auto rounded-md border border-N300">
    <FileDiff :file="file" />
  </div>
</template>
