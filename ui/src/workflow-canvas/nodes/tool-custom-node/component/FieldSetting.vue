<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolInputField, ToolInputFieldType } from '@/api/types'

defineOptions({ name: 'WorkflowToolInputFieldDialog' })

const emit = defineEmits<{ submit: [field: ToolInputField, index?: number] }>()

const inputFieldTypes: ToolInputFieldType[] = ['string', 'int', 'float', 'dict', 'array']
const formRef = useTemplateRef<FormInstance>('formRef')
const visible = ref(false)
const editing = ref(false)
const currentIndex = ref<number>()
const inputFieldForm = ref<ToolInputField>({ desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
const formRules: FormRules<ToolInputField> = {
  name: [{ required: true, message: '请输入参数名称', trigger: 'blur' }],
}

// 弹窗仅维护参数草稿，节点接收提交后关闭。
function open(field?: ToolInputField, index?: number) {
  resetData()
  if (field) {
    inputFieldForm.value = cloneDeep(field)
    editing.value = true
    currentIndex.value = index
  }
  visible.value = true
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(inputFieldForm.value), currentIndex.value))
    .catch(() => {})
}

function close() {
  visible.value = false
}

function resetData() {
  editing.value = false
  currentIndex.value = undefined
  inputFieldForm.value = { desc: '', is_required: true, name: '', source: 'reference', type: 'string' }
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <el-button text type="primary" @click="open()">
    <MkIcon name="icon_add_outlined" />
  </el-button>
  <MkDialog v-model="visible" :title="editing ? '编辑参数' : '添加参数'" @closed="resetData">
    <el-form ref="formRef" :model="inputFieldForm" :rules="formRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="参数名称" prop="name">
        <el-input
          v-model="inputFieldForm.name"
          maxlength="64"
          placeholder="请输入参数名称"
          @blur="inputFieldForm.name = inputFieldForm.name.trim()"
        />
      </el-form-item>
      <el-form-item label="数据类型">
        <el-select v-model="inputFieldForm.type" class="w-full">
          <el-option v-for="fieldType in inputFieldTypes" :key="fieldType" :label="fieldType" :value="fieldType" />
        </el-select>
      </el-form-item>
      <el-form-item label="参数说明">
        <el-input
          v-model="inputFieldForm.desc"
          maxlength="128"
          placeholder="请输入参数说明"
          show-word-limit
          @blur="inputFieldForm.desc = inputFieldForm.desc?.trim()"
        />
      </el-form-item>
      <el-form-item label="来源">
        <el-select v-model="inputFieldForm.source" class="w-full">
          <el-option label="引用参数" value="reference" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否必填" @click.prevent>
        <el-switch v-model="inputFieldForm.is_required" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
