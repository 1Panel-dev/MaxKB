<template>
  <ElPopover
    ref="popoverRef"
    :virtual-ref="currentTarget"
    virtual-triggering
    placement="top"
    :width="240"
    :show-after="0"
    :hide-after="80"
    trigger="hover"
  >
    <!-- 富文本内容，data-title 支持 HTML -->
    <div v-html="currentContent" class="sup-popover__content" />
  </ElPopover>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElPopover } from 'element-plus'

const popoverRef = ref<any>()
const currentTarget = ref<any>()
const currentContent = ref<any>('')
let hideTimer: any = null
let lastSup: any = null

function onMouseOver(e: any) {
  const sup = e.target.closest('sup[data-title]')
  if (!sup || sup === lastSup) return

  clearTimeout(hideTimer)
  lastSup = sup
  currentContent.value = sup.dataset.title
  currentTarget.value = sup
  popoverRef.value?.onOpen?.()
}

function onMouseOut(e: any) {
  const sup = e.target.closest('sup[data-title]')
  if (!sup) return

  hideTimer = setTimeout(() => {
    popoverRef.value?.onClose?.()
    lastSup = null
  }, 80)
}

onMounted(() => {
  document.addEventListener('mouseover', onMouseOver)
  document.addEventListener('mouseout', onMouseOut)
})

onUnmounted(() => {
  document.removeEventListener('mouseover', onMouseOver)
  document.removeEventListener('mouseout', onMouseOut)
  clearTimeout(hideTimer)
})
</script>
