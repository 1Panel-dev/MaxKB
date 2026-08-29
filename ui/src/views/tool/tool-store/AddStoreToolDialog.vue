<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolStoreItem } from '@/api/types'

defineOptions({ name: 'AddStoreToolDialog' })

const emit = defineEmits<{
  submit: [tool: ToolStoreItem, name: string]
}>()

interface AddStoreToolForm {
  name: string
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const currentTool = ref<ToolStoreItem>()
const addToolForm = reactive<AddStoreToolForm>({ name: '' })
const formRules: FormRules<AddStoreToolForm> = {
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid || !currentTool.value) return
    emit('submit', currentTool.value, addToolForm.name)
    visible.value = false
  })
}

function open(tool: ToolStoreItem) {
  currentTool.value = tool
  addToolForm.name = tool.name
  visible.value = true
}

function resetData() {
  currentTool.value = undefined
  addToolForm.name = ''
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="添加工具" width="450" @closed="resetData">
    <el-form
      ref="formRef"
      :model="addToolForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="addToolForm.name"
          maxlength="64"
          placeholder="请输入工具名称"
          show-word-limit
          @blur="addToolForm.name = addToolForm.name.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">添加</el-button>
    </template>
  </MkDialog>
</template>
