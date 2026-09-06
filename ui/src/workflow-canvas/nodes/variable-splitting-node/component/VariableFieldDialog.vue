<template>
  <MkDialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑变量' : '添加变量'"
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
      <el-form-item label="表达式" prop="expression">
        <template #label>
          <span class="inline-flex items-center gap-1">
            表达式
            <el-tooltip effect="dark" placement="right">
              <template #content>
                请使用 JSON Path 表达式拆分变量，例如：$.store.book
                <a
                  href="https://pypi.org/project/jsonpath-ng/1.8.0/"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:text-primary/80"
                  >点击查看详情 ➜ pypi.org</a
                >
              </template>
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
        </template>
        <el-input v-model="form.expression" :maxlength="64" show-word-limit placeholder="请输入表达式" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click.prevent="close">取消</el-button>
      <el-button type="primary" @click="submit(fieldFormRef)">保存</el-button>
    </template>
  </MkDialog>
</template>
<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'

defineOptions({ name: 'VariableSplittingFieldDialog' })

const emit = defineEmits<{ refresh: [data: { field: string; label: string; expression: string }, index?: number] }>()

const fieldFormRef = useTemplateRef<FormInstance>('fieldFormRef')
const isEdit = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const form = ref<{ field: string; label: string; expression: string }>({ field: '', label: '', expression: '' })

const rules = reactive({
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  field: [
    { required: true, message: '请输入变量', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '变量可由字母、数字、下划线组成', trigger: 'blur' },
  ],
  expression: [{ required: true, message: '请输入表达式', trigger: 'blur' }],
})

const dialogVisible = ref(false)

function open(row?: { field: string; label: string; expression: string }, index?: number) {
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
  form.value = { field: '', label: '', expression: '' }
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
