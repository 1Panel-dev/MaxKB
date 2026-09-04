<template>
  <MkDialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑分组' : '添加分组'"
    width="520px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form ref="fieldFormRef" label-position="top" require-asterisk-position="right" :rules="rules" :model="form">
      <el-form-item label="变量" prop="field">
        <el-input v-model="form.field" :maxlength="64" placeholder="请输入变量" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="form.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close">取消</el-button>
        <el-button type="primary" @click="submit(fieldFormRef)">保存</el-button>
      </span>
    </template>
  </MkDialog>
</template>
<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'VariableAggregationGroupFieldDialog' })

const emit = defineEmits<{ refresh: [data: { field: string; label: string }, index?: number] }>()

const fieldFormRef = useTemplateRef<FormInstance>('fieldFormRef')
const isEdit = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const form = ref<{ field: string; label: string }>({ field: '', label: '' })

const rules = reactive({
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  field: [
    { required: true, message: '请输入变量', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '变量可由字母、数字、下划线组成', trigger: 'blur' },
  ],
})

const dialogVisible = ref(false)

function open(data?: { field: string; label: string }, index?: number) {
  if (data) {
    form.value = cloneDeep(data)
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
<style lang="scss" scoped></style>
