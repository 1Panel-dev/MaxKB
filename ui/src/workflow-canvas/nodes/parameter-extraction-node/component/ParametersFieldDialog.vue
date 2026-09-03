<template>
  <MkDialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑参数' : '添加参数'"
    width="520px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form ref="fieldFormRef" label-position="top" require-asterisk-position="right" :rules="rules" :model="form">
      <el-form-item label="参数" prop="field" :rules="rules.field">
        <el-input v-model="form.field" :maxlength="64" placeholder="请输入参数" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label" :rules="rules.label">
        <el-input v-model="form.label" :maxlength="64" placeholder="请输入显示名称" show-word-limit />
      </el-form-item>
      <el-form-item label="参数类型" prop="parameter_type" :rules="rules.parameter_type">
        <el-select :teleported="false" v-model="form.parameter_type" placeholder="请选择参数类型" style="width: 100%">
          <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述" prop="desc">
        <el-input v-model="form.desc" type="textarea" :rows="2" placeholder="请输入描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="submit(fieldFormRef)"> 保存 </el-button>
      </span>
    </template>
  </MkDialog>
</template>
<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'ParameterExtractionFieldDialog' })

const emit = defineEmits<{ refresh: [data: Record<string, unknown>, index?: number] }>()

const options = [
  { value: 'string', label: 'string' },
  { value: 'number', label: 'number' },
  { value: 'object', label: 'object' },
  { value: 'boolean', label: 'boolean' },
  { value: 'array', label: 'array' },
]

const fieldFormRef = useTemplateRef<FormInstance>('fieldFormRef')
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const form = ref<{ field: string; label: string; parameter_type: string; desc: string }>({
  field: '',
  label: '',
  parameter_type: '',
  desc: '',
})

const rules = reactive({
  field: [
    { required: true, message: '请输入参数', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '参数可由字母、数字、下划线组成', trigger: 'blur' },
  ],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  parameter_type: [{ required: true, message: '请选择参数类型', trigger: 'change' }],
})

function resetForm() {
  form.value = { field: '', label: '', parameter_type: '', desc: '' }
}

function open(row?: Record<string, unknown>, index?: number) {
  resetForm()
  if (row) {
    form.value = cloneDeep(row as typeof form.value)
    isEdit.value = true
    currentIndex.value = index
  }
  dialogVisible.value = true
}

function close() {
  dialogVisible.value = false
  isEdit.value = false
  currentIndex.value = undefined
  resetForm()
}

const submit = async (formEl: FormInstance | null) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', cloneDeep(form.value), currentIndex.value)
    }
  })
}

defineExpose({ open, close })
</script>
