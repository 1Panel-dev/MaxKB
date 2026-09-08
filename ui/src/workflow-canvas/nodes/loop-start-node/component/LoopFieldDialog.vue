<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormRules, FormInstance } from 'element-plus'
import { isLoopBuiltinField } from '../constant'

defineOptions({ name: 'LoopFieldDialog' })

type LoopInputField = { field: string; label: string }
const emit = defineEmits<{ submit: [data: LoopInputField, index?: number] }>()

// 参数表单与校验。
const fieldFormRef = ref<FormInstance>()
const form = ref<LoopInputField>({ field: '', label: '' })
const rules: FormRules<LoopInputField> = {
  field: [
    { required: true, message: '请输入参数', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '参数只能包含英文字母、数字、下划线', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (isLoopBuiltinField(value)) {
          callback(new Error('此参数为循环引擎内置，不可使用'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
}

// 打开时初始化，关闭动画结束后清理编辑状态。
const dialogVisible = ref(false)
const currentIndex = ref<number>()
const isEdit = computed(() => currentIndex.value !== undefined)

function open(row?: LoopInputField, index?: number) {
  form.value = row ? cloneDeep(row) : { field: '', label: '' }
  currentIndex.value = index
  dialogVisible.value = true
}

function close() {
  dialogVisible.value = false
}

function resetData() {
  currentIndex.value = undefined
  form.value = { field: '', label: '' }
  fieldFormRef.value?.clearValidate()
}

// 表格负责重名检查、写回和成功后的关闭。
async function submit() {
  const valid = await fieldFormRef.value?.validate().catch(() => false)
  if (!valid) return
  emit('submit', cloneDeep(form.value), currentIndex.value)
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog :title="isEdit ? '编辑参数' : '添加参数'" v-model="dialogVisible" align-center @closed="resetData">
    <el-form label-position="top" ref="fieldFormRef" :rules="rules" :model="form" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="参数" prop="field">
        <el-input v-model="form.field" :maxlength="64" placeholder="请输入参数" show-word-limit />
      </el-form-item>
      <el-form-item label="显示名称" prop="label">
        <el-input v-model="form.label" :maxlength="64" show-word-limit placeholder="请输入显示名称" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="submit">{{ isEdit ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
