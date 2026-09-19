<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { Top } from '@element-plus/icons-vue'
import type { InputInstance } from 'element-plus'

defineOptions({ name: 'ChatInput' })

const props = withDefaults(
  defineProps<{
    modelValue?: string
    disabled?: boolean
    placeholder?: string
    maxlength?: number
    loading?: boolean
    submitDisabled?: boolean
    pasteAsText?: boolean
  }>(),
  {
    modelValue: '',
    disabled: false,
    placeholder: '输入消息...',
    loading: false,
    submitDisabled: false,
    pasteAsText: false,
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'paste-images': [files: File[]]
  'paste-videos': [files: File[]]
  'paste-files': [files: File[]]
  'paste-text': [text: string]
  submit: []
  stop: []
  focus: []
  blur: []
}>()

// 输入与操作共用提交条件，文本域高度交由 Element Plus 管理。
const textareaRef = useTemplateRef<InputInstance>('textareaRef')
const inputText = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
})
const cannotSubmit = computed(() => props.disabled || props.submitDisabled || props.loading || !inputText.value.trim())

function submit() {
  if (!cannotSubmit.value) emit('submit')
}

function onKeydown(event: KeyboardEvent) {
  if (event.isComposing || event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  submit()
}

// 保留附件粘贴事件；纯文本场景使用浏览器原生粘贴和长度限制。
const LONG_TEXT_THRESHOLD = 300
const onPaste = (event: ClipboardEvent) => {
  if (props.pasteAsText) return
  const items = event.clipboardData?.items
  if (!items) return

  const fileItems = Array.from(items)
    .filter((item) => item.kind === 'file')
    .map((item) => item.getAsFile())
    .filter(Boolean) as File[]

  if (fileItems.length) {
    event.preventDefault()

    const images = fileItems.filter((f) => f.type.startsWith('image/'))
    const videos = fileItems.filter((f) => f.type.startsWith('video/'))
    const others = fileItems.filter((f) => !f.type.startsWith('image/') && !f.type.startsWith('video/'))

    if (images.length) emit('paste-images', images)
    if (videos.length) emit('paste-videos', videos)
    if (others.length) emit('paste-files', others)
    return
  }

  const text = event.clipboardData?.getData('text/plain') || ''
  if (text.length > LONG_TEXT_THRESHOLD) {
    event.preventDefault()
    emit('paste-text', text)
  }
}

function clear() {
  inputText.value = ''
}

function focus() {
  textareaRef.value?.focus()
}

defineExpose({ clear, focus })
</script>

<template>
  <div class="chat-input min-w-0 flex-1 overflow-hidden rounded-xl border bg-white" :class="{ 'is-disabled': disabled }">
    <el-input
      ref="textareaRef"
      v-model="inputText"
      type="textarea"
      resize="none"
      :autosize="{ minRows: 1, maxRows: 10 }"
      :disabled="disabled"
      :placeholder="placeholder"
      :maxlength="maxlength"
      @keydown="onKeydown"
      @focus="emit('focus')"
      @blur="emit('blur')"
      @paste="onPaste"
    />
    <!-- // TODO 样式 -->
    <div class="flex justify-end px-2 pb-2 pt-1">
      <!-- 停止生成 -->
      <el-button v-if="loading" class="input-action" circle type="primary" :disabled="disabled" @click="emit('stop')">
        <MkIcon name="icon_stop_filled" />
      </el-button>
      <!-- 发送输入内容 -->
      <el-button v-else class="input-action" circle type="primary" :disabled="cannotSubmit" @click="submit">
        <MkIcon :icon="Top" :size="16" />
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* 输入区与操作栏 */
.chat-input {
  transition: border-color 0.2s;

  &:not(.is-disabled):hover,
  &:not(.is-disabled):focus-within {
    border-color: var(--mk-primary);
  }

  :deep(.el-textarea__inner) {
    background: transparent;
    border-radius: 0;
    box-shadow: none;
    padding: calc(var(--spacing) * 2) calc(var(--spacing) * 2) 0;
  }

  .input-action {
    height: calc(var(--spacing) * 6);
    min-height: 0;
    padding: 0;
    width: calc(var(--spacing) * 6);

    &.is-disabled {
      background-color: var(--mk-N400);
      border-color: var(--mk-N400);
    }
  }
}
</style>
