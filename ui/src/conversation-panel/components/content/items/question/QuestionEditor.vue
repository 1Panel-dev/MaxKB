<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { InputInstance } from 'element-plus'

defineOptions({ name: 'ConversationQuestionEditor' })

const props = defineProps<{ content: string; disabled: boolean }>()
const emit = defineEmits<{ cancel: []; send: [question: string] }>()

// 每次进入编辑模式创建草稿，取消时随组件卸载丢弃。
const questionDraft = ref(props.content)
const editorRef = ref<InputInstance>()
onMounted(() => editorRef.value?.focus())

function sendQuestion() {
  if (!props.disabled && questionDraft.value.trim()) emit('send', questionDraft.value)
}
</script>

<template>
  <div class="space-y-3">
    <!-- 编辑提问正文 -->
    <el-input
      ref="editorRef"
      v-model="questionDraft"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 8 }"
      resize="none"
      class="question-editor-input"
    />
    <div class="flex justify-end gap-3">
      <!-- 取消编辑 -->
      <el-button class="min-w-20" @click="emit('cancel')">取消</el-button>
      <!-- 发送编辑后的提问 -->
      <el-button type="primary" class="min-w-20" :disabled="disabled || !questionDraft.trim()" @click="sendQuestion">发送</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.question-editor-input :deep(.el-textarea__inner) {
  padding: 0;
  box-shadow: none;
  background: transparent;
}
</style>
