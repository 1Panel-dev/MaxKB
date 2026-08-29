<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'AddInternalToolDialog' })

const props = defineProps<{
  api: typeof ToolApi
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
}>()

interface InternalToolForm {
  name: string
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const editId = ref<string>()
const isEdit = ref(false)
const internalToolForm = reactive<InternalToolForm>({ name: '' })
const formRules: FormRules<InternalToolForm> = {
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
}

function handleSubmit() {
  void formRef.value?.validate((valid) => {
    if (!valid || !editId.value) return

    loading.value = true
    props.api
      .putTool(editId.value, { name: internalToolForm.name })
      .then(() => {
        MsgSuccess('保存成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => (loading.value = false))
  })
}

function open(tool: ToolItem, edit = false) {
  editId.value = tool.id
  isEdit.value = edit
  internalToolForm.name = tool.name
  visible.value = true
}

function handleClosed() {
  editId.value = undefined
  isEdit.value = false
  internalToolForm.name = ''
  formRef.value?.clearValidate()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="isEdit ? '编辑工具' : '添加工具'"
    width="450"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="internalToolForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="internalToolForm.name"
          maxlength="64"
          placeholder="请输入工具名称"
          show-word-limit
          @blur="internalToolForm.name = internalToolForm.name.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '保存' : '添加' }}
      </el-button>
    </template>
  </MkDialog>
</template>
