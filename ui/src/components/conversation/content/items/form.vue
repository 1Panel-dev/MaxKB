<template>
  <div class="content-form">
    <DynamicsForm
      :disabled="is_submit"
      label-position="top"
      require-asterisk-position="right"
      ref="dynamicsFormRef"
      :render_data="form_field_list"
      label-suffix=":"
      v-model="form_data"
      :model="form_data"
    />
    <el-button :type="is_submit ? 'info' : 'primary'" :disabled="is_submit" @click="submit">
      {{ is_submit ? '已提交' : '提交' }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, inject } from 'vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'

const chat = inject<any>('chat')

const props = defineProps<{
  content: any
}>()

const _submit = ref(false)
const form_field_list = computed(() => props.content.form_field_list || [])
const is_submit = computed(() => _submit.value || !!props.content.is_submit)
const _form_data = ref<any>({})
const form_data = computed({
  get: () => (props.content.is_submit ? props.content.form_data : _form_data.value),
  set: (v) => {
    _form_data.value = v
  }
})
const dynamicsFormRef = ref()

const submit = async () => {
  try {
    await dynamicsFormRef.value?.validate()
    _submit.value = true
    
    if (chat?.sendMessage) {
      // 确保有对话 ID
      if (!chat.currentChatId?.value && chat?.openChat) {
        await chat.openChat()
      }
      
      // 传递 position、chat_record_id、chunk_id
      const position = props.content.position || null
      const chatRecordId = props.content.chat_record_id || null
      const chunkId = props.content.id || null
      
      // form_data 只包含表单收集到的数据
      const formData = { ...form_data.value }
      
      // 使用 form_content_format 作为消息
      const message = props.content.form_content_format || '表单已提交'
      
      await chat.sendMessage(message, { 
        re_chat: true, 
        form_data: formData,
        position: position,
        chat_record_id: chatRecordId,
        chunk_id: chunkId,
        onScroll: () => chat.scrollToBottom?.()
      })
    }
  } catch (e) {
    console.error('Form submit failed:', e)
    _submit.value = false
  }
}
</script>

<style scoped>
.content-form {
  background: #ffffff;
  border: 1px solid var(--el-border-color-lighter, #e4e7ed);
  border-radius: 8px;
  padding: 16px;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}
</style>
