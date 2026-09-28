<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, useId, useTemplateRef, watch } from 'vue'
import { ElOverlay, TrapFocus as vTrapFocus, useLockscreen, useZIndex, type ButtonInstance } from 'element-plus'
import type { MediaPreviewProps } from './types'

defineOptions({ name: 'MkMediaPreview' })
const props = defineProps<MediaPreviewProps>()
defineSlots<{ default(): unknown; player(): unknown }>()
const visible = ref(false)
const triggerRef = useTemplateRef<HTMLDivElement>('triggerRef')
const closeButtonRef = useTemplateRef<ButtonInstance>('closeButtonRef')
const overlayZIndex = ref(0)
const { nextZIndex } = useZIndex()
useLockscreen(visible)
const titleId = useId()

// 复用 Element Plus 遮罩、层级、滚动锁定和焦点约束。
function open() {
  if (!props.src || visible.value) return
  overlayZIndex.value = nextZIndex()
  visible.value = true
  void nextTick(() => closeButtonRef.value?.ref?.focus())
}

function close() {
  if (!visible.value) return
  visible.value = false
  triggerRef.value?.focus()
}

// 地址变化或组件卸载时关闭预览并停止播放。
watch(() => props.src, close)
onBeforeUnmount(close)
</script>

<template>
  <div ref="triggerRef" role="button" :tabindex="src ? 0 : -1" @click="open" @keydown.enter.stop.prevent="open" @keydown.space.stop.prevent="open">
    <slot />
  </div>

  <Teleport to="body">
    <el-overlay v-if="visible" :z-index="overlayZIndex" @click="close">
      <div
        v-trap-focus
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        class="flex-center min-h-full p-6"
        @click.self="close"
        @keydown.esc.stop.prevent="close"
      >
        <!-- 关闭媒体预览 -->
        <el-button ref="closeButtonRef" circle size="large" type="info" class="mk-media-preview-close absolute right-6 top-6" @click="close">
          <MkIcon name="icon_close_outlined" :size="22" />
        </el-button>
        <div class="w-full max-w-240 min-w-0">
          <div class="flex-center">
            <slot name="player" />
          </div>
        </div>
      </div>
    </el-overlay>
  </Teleport>
</template>

<style scoped lang="scss">
.mk-media-preview-close {
  &,
  &:hover,
  &:active {
    border: rgb(var(--mk-N900-rgb) / 80%);
    background-color: rgb(var(--mk-N900-rgb) / 80%);
    color: white;
  }
}
</style>
