<template>
  <el-dialog
    :title="isEdit ? '编辑参数' : '添加参数'"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <el-form label-position="top" ref="fieldFormRef" :rules="rules" :model="form" require-asterisk-position="right">
      <el-form-item label="参数名" required prop="field" :rules="rules.field">
        <el-input v-model="form.field" :maxlength="64" placeholder="请输入变量名（英文字母、数字、下划线）" show-word-limit />
      </el-form-item>
      <el-form-item label="参数标签" required prop="label" :rules="rules.label">
        <el-input v-model="form.label" :maxlength="64" show-word-limit placeholder="请输入参数标签" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close">取消</el-button>
        <el-button type="primary" @click="submit(fieldFormRef)">{{ isEdit ? '保存' : '添加' }}</el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { isLoopBuiltinField } from '../constant'

defineOptions({ name: 'LoopFieldDialog' })
const emit = defineEmits<{ refresh: [data: { field: string; label: string }, index?: number] }>()

const fieldFormRef = ref<FormInstance>()
const isEdit = ref(false)
const currentIndex = ref<number>()
const form = ref<{ field: string; label: string }>({ field: '', label: '' })

const rules = reactive({
  label: [{ required: true, message: '请输入参数标签', trigger: 'blur' }],
  field: [
    { required: true, message: '请输入变量名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '变量名只能包含英文字母、数字、下划线', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (isLoopBuiltinField(value)) {
          callback(new Error('此变量名为循环引擎内置，不可使用'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

const dialogVisible = ref(false)

function open(row?: { field: string; label: string }, index?: number) {
  if (row) {
    form.value = cloneDeep(row)
    isEdit.value = true
    currentIndex.value = index
  }
  dialogVisible.value = true
}

function close() {
  dialogVisible.value = false
  isEdit.value = false
  currentIndex.value = undefined
  form.value = { field: '', label: '' }
}

async function submit(formEl: FormInstance | undefined) {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value, currentIndex.value)
    }
  })
}

defineExpose({ open, close })
</script>
