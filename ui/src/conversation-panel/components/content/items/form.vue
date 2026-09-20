<template>
  <div class="content-form">
    <MdPreview class="!h-auto" editorId="conversation-text" :modelValue="leadingText || ''"></MdPreview>
    <MkDynamicsForm ref="dynamicsFormRef" :view="is_submit" :render-data="form_field_list" v-model="form_data" />
    <MdPreview class="!h-auto" editorId="conversation-text" :modelValue="trailingText || ''"></MdPreview>
    <el-button :type="is_submit ? 'info' : 'primary'" :disabled="is_submit || !mainStore" @click="submit">
      {{ is_submit ? '已提交' : '提交' }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import { useMessageListStoreOptional } from '@/conversation-panel/components/message-list/index'

// message-list store(由 view provide);拿不到发送能力 → 只读降级
const mainStore = useMessageListStoreOptional()

const props = defineProps<{
  content: any
}>()
const form_content_format = computed(() => props.content.form_content_format)
const _submit = ref(false)
const form_field_list = computed(() => props.content.form_field_list || [])
const [leadingText, trailingText] = form_content_format.value.split('{{form}}').map((s) => s.trim())

const is_submit = computed(() => _submit.value || !!props.content.is_submit)
const _form_data = ref<any>({})
const form_data = computed({
  get: () => (props.content.is_submit ? props.content.form_data : _form_data.value),
  set: (v) => {
    _form_data.value = v
  },
})
const dynamicsFormRef = ref()

// 表单重提交是对同一条 chat_record 的续跑（newQuestion=false）：
// 不新增 question，续跑分片由 chat-panel 聚合回持有本表单的那条 assistant 消息。
const submit = async () => {
  try {
    await dynamicsFormRef.value?.validate()
    _submit.value = true
    mainStore?.sendMessage({
      message: { content: '', type: 'QUESTION' },
      newQuestion: false,
      reChat: true,
      formData: { ...form_data.value },
      position: props.content.position || null,
      chatRecordId: props.content.chat_record_id || null,
      chunkId: props.content.id || null,
    })
  } catch (e) {
    console.error('Form submit failed:', e)
    _submit.value = false
  }
}
</script>

<style scoped lang="scss"></style>
