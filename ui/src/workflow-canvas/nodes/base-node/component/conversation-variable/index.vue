<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { Delete, Edit } from '@element-plus/icons-vue'
import { MsgError } from '@/utils/message'
import type { ChatInputField } from '../../types'

defineOptions({ name: 'BaseNodeConversationVariable' })

const props = defineProps<{ fields: ChatInputField[] }>()
const emit = defineEmits<{ 'update:fields': [fields: ChatInputField[]] }>()

const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ChatInputField>({ field: '', label: '' })

function openDialog(field?: ChatInputField, index?: number) {
  editingIndex.value = index
  currentField.value = cloneDeep(field ?? { field: '', label: '' })
  dialogVisible.value = true
}

function submitField() {
  formRef.value?.validate().then(() => {
    const field = cloneDeep(currentField.value)
    if (props.fields.some((item, index) => item.field === field.field && index !== editingIndex.value)) {
      MsgError(`参数已存在：${field.field}`)
      return
    }

    const fields = [...props.fields]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    emit('update:fields', fields)
    dialogVisible.value = false
  })
}

function deleteField(index: number) {
  emit(
    'update:fields',
    props.fields.filter((_field, fieldIndex) => fieldIndex !== index),
  )
}
</script>

<template>
  <section>
    <div class="flex-between mb-3">
      <h6>会话变量</h6>
      <el-button link type="primary" @click="openDialog()"><MkIcon name="icon_add_outlined" />添加</el-button>
    </div>
    <el-table v-if="fields.length" :data="fields" class="mb-4" table-layout="fixed">
      <el-table-column label="参数" prop="field" show-overflow-tooltip />
      <el-table-column label="显示名称" prop="label" show-overflow-tooltip />
      <el-table-column label="操作" width="88">
        <template #default="{ row, $index }">
          <el-button link type="primary" title="编辑" @click="openDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <MkDialog v-model="dialogVisible" :title="editingIndex === undefined ? '添加会话变量' : '编辑会话变量'" width="560">
    <el-form ref="formRef" :model="currentField" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        label="参数"
        prop="field"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input v-model="currentField.field" maxlength="64" show-word-limit @blur="currentField.field = currentField.field.trim()" />
      </el-form-item>
      <el-form-item label="显示名称" prop="label" :rules="{ required: true, message: '请输入显示名称', trigger: 'blur' }">
        <el-input v-model="currentField.label" maxlength="64" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
