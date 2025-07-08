<template>
  <el-dialog class="responsive-dialog" :title="$t('chat.editTitle')" v-model="dialogVisible"
    :close-on-click-modal="false" :close-on-press-escape="false" :destroy-on-close="true" append-to-body>
    <el-form label-position="top" ref="fieldFormRef" :model="form" require-asterisk-position="right">
      <el-form-item prop="abstract" :rules="[
        {
          required: true,
          message: $t('common.inputPlaceholder'),
          trigger: 'blur'
        }
      ]">
        <el-input v-model="form.abstract" maxlength="1024" show-word-limit type="textarea"
          @blur="form.abstract = form.abstract.trim()" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import chatAPI from '@/api/chat/chat'
const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const applicationId = ref<string>('')
const chatId = ref<string>('')

const form = ref<any>({
  abstract: ''
})

const dialogVisible = ref<boolean>(false)

const open = (row: any, id: string) => {
  applicationId.value = id
  chatId.value = row.id
  form.value.abstract = row.abstract
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {

  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      chatAPI.modifyChat(chatId.value, form.value, loading).then(() => {
        emit('refresh', chatId.value, form.value.abstract)
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
