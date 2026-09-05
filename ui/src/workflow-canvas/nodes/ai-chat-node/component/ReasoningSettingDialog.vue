<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ReasoningSetting } from '../types'

defineOptions({ name: 'AiChatNodeReasoningSettingDialog' })

const emit = defineEmits<{ submit: [setting: ReasoningSetting] }>()

const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<ReasoningSetting>({
  reasoning_content_enable: false,
  reasoning_content_end: '</think>',
  reasoning_content_start: '<think>',
})

function open(setting: ReasoningSetting) {
  formData.value = cloneDeep(setting)
  visible.value = true
}

function submit() {
  formRef.value?.validate().then(() => {
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="思考过程设置" width="560">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-alert
        class="mb-3"
        :closable="false"
        show-icon
        title="当模型未单独返回 reasoning_content 时，将使用开始和结束标签从回答中提取思考过程。"
        type="info"
      />
      <el-form-item label="开始标签" prop="reasoning_content_start" :rules="{ required: true, message: '请输入开始标签', trigger: 'blur' }">
        <el-input v-model="formData.reasoning_content_start" placeholder="例如：<think>" />
      </el-form-item>
      <el-form-item label="结束标签" prop="reasoning_content_end" :rules="{ required: true, message: '请输入结束标签', trigger: 'blur' }">
        <el-input v-model="formData.reasoning_content_end" placeholder="例如：</think>" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
