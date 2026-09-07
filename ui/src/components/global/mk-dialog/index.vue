<script setup lang="ts">
import { ref, watch } from 'vue'

defineOptions({ name: 'MkDialog', inheritAttrs: false })

const props = withDefaults(defineProps<{ contentClass?: string; destroyOnClose?: boolean }>(), {
  destroyOnClose: true,
})

const visible = defineModel<boolean>({ default: false })

// 打开时才挂载弹窗，关闭动画结束后再释放外壳，保留 closed 事件和表单清理。
const rendered = ref(visible.value)
watch(visible, (value) => {
  if (value) rendered.value = true
})

function handleClosed() {
  if (props.destroyOnClose) rendered.value = false
}

defineSlots<{
  default(): unknown
  footer(): unknown
  header(props: { close: () => void; titleClass: string; titleId: string }): unknown
  subtitle(): unknown
}>()
</script>

<template>
  <el-dialog
    v-if="rendered"
    v-model="visible"
    :append-to-body="true"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="props.destroyOnClose"
    :show-close="true"
    :width="600"
    v-bind="$attrs"
    @closed="handleClosed"
  >
    <template v-if="$slots.header || $slots.subtitle" #header="{ close, titleClass, titleId }">
      <div class="min-w-0 flex-1">
        <slot v-if="$slots.header" name="header" :close="close" :title-class="titleClass" :title-id="titleId" />
        <span v-else :id="titleId" :class="titleClass">{{ $attrs.title }}</span>
        <p v-if="$slots.subtitle" class="mt-2 text-N600">
          <slot name="subtitle" />
        </p>
      </div>
    </template>

    <el-scrollbar>
      <div class="px-6 dialog-content" :class="props.contentClass">
        <slot />
      </div>
    </el-scrollbar>

    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </el-dialog>
</template>
