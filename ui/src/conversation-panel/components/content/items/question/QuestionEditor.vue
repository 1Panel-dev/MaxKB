<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { InputInstance } from 'element-plus'
import { useInputEvents } from '../../../../core/input-events'

defineOptions({ name: 'ConversationQuestionEditor' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ content: string; disabled: boolean }>()
const emit = defineEmits<{ cancel: []; send: [question: string] }>()

// 每次进入编辑模式创建草稿，取消时随组件卸载丢弃。
const questionDraft = ref(props.content)
const editorRef = ref<InputInstance>()
onMounted(() => editorRef.value?.focus())

function sendQuestion() {
  if (!props.disabled && questionDraft.value.trim()) emit('send', questionDraft.value)
}

// 回车发送、组合键换行，与消息输入框一致；编辑框不接收附件。
const { handleKeydown } = useInputEvents({ text: questionDraft, canUpload: () => false, addFiles: () => {}, submit: sendQuestion })
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
      @keydown.enter="handleKeydown"
    />
    <div class="flex justify-end">
      <!-- 取消编辑；提交请求期间禁用，避免编辑框关闭后提问仍被发送 -->
      <el-button plain class="min-w-20" :disabled="disabled" @click="emit('cancel')">{{ t('common.actions.cancel') }}</el-button>
      <!-- 发送编辑后的提问 -->
      <el-button type="primary" class="min-w-20" :disabled="disabled || !questionDraft.trim()" @click="sendQuestion">
        {{ t('common.actions.send') }}
      </el-button>
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
