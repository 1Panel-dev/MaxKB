<template>
  <el-dialog
    :title="isEdit ? '编辑参数' : '添加参数'"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    append-to-body
  >
    <DynamicsFormConstructor
      v-model="currentItem"
      label-position="top"
      require-asterisk-position="right"
      :input_type_list="inputTypeList"
      ref="DynamicsFormConstructorRef"
    ></DynamicsFormConstructor>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { cloneDeep } from 'lodash'
import DynamicsFormConstructor from '@/components/dynamics-form/constructor/index.vue'
import type { FormField } from '@/components/dynamics-form/type'

const emit = defineEmits(['refresh'])

const DynamicsFormConstructorRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)
const currentItem = ref<FormField>()
const currentIndex = ref(null)
const inputTypeList = ref([
  { label: '文本框', value: 'TextInputConstructor' },
  { label: '单选框', value: 'SingleSelectConstructor' },
  { label: '日期', value: 'DatePickerConstructor' }
])

const dialogVisible = ref<boolean>(false)


const open = (row: any, index: any) => {
  dialogVisible.value = true

  if (row) {
    isEdit.value = true
    currentItem.value = cloneDeep(row)
    currentIndex.value = index

    // 新版本已经上线
    if (row.input_type) {
      return
    }
    // 旧版本数据兼容
    switch (row.type) {
      case 'input':
        currentItem.value = {
          field: row.field || row.variable,
          input_type: 'TextInput',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required || row.is_required
        }
        break
      case 'select':
        currentItem.value = {
          field: row.field || row.variable,
          input_type: 'SingleSelect',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required || row.is_required,
          option_list: row.optionList.map((o: any) => {
            return { key: o, value: o }
          })
        }
        break
      case 'date':
        currentItem.value = {
          field: row.field || row.variable,
          input_type: 'DatePicker',
          label: row.label || row.name,
          default_value: row.default_value,
          required: row.required || row.is_required,
          attrs: {
            format: 'YYYY-MM-DD HH:mm:ss',
            'value-format': 'YYYY-MM-DD HH:mm:ss',
            type: 'datetime'
          }
        }
        break
      default:
        break
    }
  }
}

const close = () => {
  dialogVisible.value = false
  isEdit.value = false
  currentIndex.value = null
  currentItem.value = null as any
}

const submit = async () => {
  const formEl = DynamicsFormConstructorRef.value
  if (!formEl) return
  await formEl.validate().then(() => {
    emit('refresh', formEl?.getData(), currentIndex.value)
    isEdit.value = false
    currentItem.value = null as any
    currentIndex.value = null
  })
}


defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
