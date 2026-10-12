<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ParagraphCreatePayload } from '@/api/types'

defineOptions({ name: 'CreateParagraphDialog' })
const props = defineProps<{ loading: boolean }>()
const emit = defineEmits<{ submit: [payload: ParagraphCreatePayload]; closed: [] }>()

/* 新增分段草稿：关闭后由页面卸载，失败保留输入。 */
const visible = ref(false)
const formRef = ref<FormInstance>()
const paragraphForm = ref<ParagraphCreatePayload>({ title: '', content: '', is_active: true })
const paragraphRules: FormRules<ParagraphCreatePayload> = {
  title: [{ max: 256, message: '标题最多 256 字符', trigger: 'blur' }],
  content: [
    { required: true, whitespace: true, message: '请输入分段内容', trigger: 'blur' },
    { max: 102400, message: '内容最多 102400 字符', trigger: 'blur' },
  ],
}

function handleSubmit() {
  if (props.loading) return
  void formRef.value
    ?.validate()
    .then(() => {
      if (props.loading) return
      emit('submit', { ...paragraphForm.value, title: paragraphForm.value.title.trim() })
    })
    .catch(() => {})
}

function handleBeforeClose(done: () => void) {
  if (!props.loading) done()
}

defineExpose({
  open: () => {
    visible.value = true
  },
  close: () => {
    visible.value = false
  },
})
</script>

<template>
  <MkDialog v-model="visible" title="添加分段" width="800" :before-close="handleBeforeClose" @closed="emit('closed')">
    <el-form ref="formRef" v-loading="loading" :model="paragraphForm" :rules="paragraphRules" label-position="top" @submit.prevent>
      <el-form-item label="标题" prop="title">
        <el-input v-model="paragraphForm.title" maxlength="256" placeholder="请输入标题" show-word-limit />
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input v-model="paragraphForm.content" type="textarea" :rows="10" maxlength="102400" placeholder="请输入分段内容，支持 Markdown" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消添加分段 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 保存新增分段 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">添加</el-button>
    </template>
  </MkDialog>
</template>
