<template>
  <div class="md-editor" :class="{ focused: isFocused }">
    <textarea
      ref="textareaRef"
      v-model="inputText"
      :disabled="disabled"
      :placeholder="placeholder"
      @keydown="onKeydown"
      @input="onInput"
      @focus="isFocused = true; emit('focus')"
      @blur="isFocused = false; emit('blur')"
      @paste="onPaste"
      rows="1"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    disabled?: boolean
    placeholder?: string
  }>(),
  {
    modelValue: '',
    disabled: false,
    placeholder: '输入消息...'
  }
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'paste-images': [files: File[]]
  'paste-videos': [files: File[]]
  'paste-files': [files: File[]]
  'paste-text': [text: string]
  submit: []
  focus: []
  blur: []
}>()

const LONG_TEXT_THRESHOLD = 300

const isFocused = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const inputText = ref(props.modelValue)

watch(
  () => props.modelValue,
  (val) => {
    if (val !== inputText.value) {
      inputText.value = val
    }
  }
)

const onInput = () => {
  emit('update:modelValue', inputText.value)
  adjustHeight()
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    emit('submit')
  }
}

const onPaste = (event: ClipboardEvent) => {
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
    const others = fileItems.filter(
      (f) => !f.type.startsWith('image/') && !f.type.startsWith('video/')
    )

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

const adjustHeight = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

const clear = () => {
  inputText.value = ''
  emit('update:modelValue', '')
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

const focus = () => {
  textareaRef.value?.focus()
}

onMounted(() => {
  adjustHeight()
})

defineExpose({ clear, focus })
</script>

<style scoped lang="scss">
.md-editor {
  flex: 1;
  min-width: 0;
}

.md-editor textarea {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  background: transparent;
  color: var(--t1, #303133);
  min-height: 24px;
  max-height: 160px;
  padding: 4px 0;
  word-break: break-word;
}

.md-editor textarea::placeholder {
  color: var(--t3, #909399);
}
</style>
