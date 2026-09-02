<template>
  <div class="content-form">
    <MkDynamicsForm ref="dynamicsFormRef" :view="is_submit" :render-data="form_field_list" v-model="form_data" />
    <el-button :type="is_submit ? 'info' : 'primary'" :disabled="is_submit" @click="submit">
      {{ is_submit ? '已提交' : '提交' }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, inject } from 'vue'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'

// 由 chat-panel 注入的通用「发起对话」函数
const sendMessage = inject<(opts: any) => void>('sendMessage')

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
  },
})
const dynamicsFormRef = ref()

// 表单重提交是对同一条 chat_record 的续跑（newQuestion=false）：
// 不新增 question，续跑分片由 chat-panel 聚合回持有本表单的那条 assistant 消息。
const submit = async () => {
  try {
    await dynamicsFormRef.value?.validate()
    _submit.value = true
    sendMessage?.({
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
