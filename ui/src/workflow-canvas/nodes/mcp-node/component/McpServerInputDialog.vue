<template>
  <MkDialog v-model="dialogVisible" title="设置变量">
    <el-form ref="formRef" label-position="top" :model="form" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        v-for="item in inputFieldList"
        :key="item"
        :label="item"
        :prop="item"
        :rules="{ required: true, message: '该项必填', trigger: 'blur' }"
      >
        <el-input v-model="form[item]" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit(formRef)">保存</el-button>
      </span>
    </template>
  </MkDialog>
</template>
<script setup lang="ts">
import { ref, useTemplateRef, reactive } from 'vue'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'McpServerInputDialog' })

const emit = defineEmits<{ refresh: [value: Record<string, string>] }>()

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<Record<string, string>>({})

const inputFieldList = ref<string[]>([])

function open(vars: string[]) {
  Object.keys(form).forEach((key) => delete form[key])
  inputFieldList.value = vars
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | null) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', { ...form })
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
