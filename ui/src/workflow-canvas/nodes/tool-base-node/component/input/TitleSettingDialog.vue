<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import type { ToolFieldConfig } from '../../types'

const emit = defineEmits<{ submit: [data: ToolFieldConfig] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const dialogVisible = ref(false)
const form = ref<ToolFieldConfig>({ title: '用户输入' })

function resetData() {
  form.value = { title: '用户输入' }
  formRef.value?.clearValidate()
}

function open(config: ToolFieldConfig) {
  resetData()
  form.value = cloneDeep(config)
  dialogVisible.value = true
}

function submitTitle() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(form.value)))
    .catch(() => {})
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="设置" align-center  @closed="resetData">
    <el-form ref="formRef" :model="form" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="标题" prop="title" :rules="[{ required: true, message: '请输入标题', trigger: 'blur' }]">
        <el-input v-model="form.title" maxlength="64" show-word-limit @blur="form.title = form.title.trim()" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消设置 -->
      <el-button @click="dialogVisible = false">取消</el-button>
      <!-- 保存标题 -->
      <el-button type="primary" @click="submitTitle">保存</el-button>
    </template>
  </MkDialog>
</template>
