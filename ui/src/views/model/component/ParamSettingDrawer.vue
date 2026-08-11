<template>
  <el-drawer
    v-model="drawerVisible"
    direction="rtl"
    size="480"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
  >
    <template #header>
      <h4 class="m-0">{{ isEdit ? '编辑参数' : '添加参数' }}</h4>
    </template>

    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right">
      <el-form-item label="参数名称" prop="label" :rules="[{ required: true, message: '请输入参数名称', trigger: 'blur' }]">
        <el-input v-model="formData.label" placeholder="请输入参数名称" />
      </el-form-item>

      <el-form-item label="字段名" prop="field" :rules="[{ required: true, message: '请输入字段名', trigger: 'blur' }]">
        <el-input v-model="formData.field" placeholder="请输入字段名" />
      </el-form-item>

      <el-form-item label="输入类型" prop="input_type" :rules="[{ required: true, message: '请选择输入类型', trigger: 'change' }]">
        <el-select v-model="formData.input_type" style="width: 100%" placeholder="请选择输入类型">
          <el-option v-for="item in inputTypes" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>

      <el-form-item label="默认值" prop="default_value">
        <el-input v-model="formData.default_value" placeholder="请输入默认值" />
      </el-form-item>

      <el-form-item label="必填" prop="required">
        <el-switch v-model="formData.required" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="confirm">{{ isEdit ? '保存' : '添加' }}</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const inputTypes = [
  { label: '文本输入', value: 'TextInput' },
  { label: '密码输入', value: 'PasswordInput' },
  { label: '文本域', value: 'TextareaInput' },
  { label: '单选框', value: 'SingleSelect' },
  { label: '开关', value: 'SwitchInput' },
  { label: '滑块', value: 'Slider' },
  { label: '单选按钮', value: 'RadioRow' },
  { label: '滑动输入', value: 'RadioButton' },
]

const drawerVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref<any>(null)
const formRef = ref()
const formData = reactive({
  label: '',
  field: '',
  input_type: 'TextInput',
  default_value: '',
  required: false,
})

const emit = defineEmits<{
  (e: 'confirm', data: any, index: any): void
}>()

function open(data?: any, index?: any) {
  if (data) {
    isEdit.value = true
    editIndex.value = index
    formData.label = data.label || ''
    formData.field = data.field || ''
    formData.input_type = data.input_type || 'TextInput'
    formData.default_value = data.default_value ?? ''
    formData.required = data.required ?? false
  } else {
    isEdit.value = false
    editIndex.value = null
    formData.label = ''
    formData.field = ''
    formData.input_type = 'TextInput'
    formData.default_value = ''
    formData.required = false
  }
  drawerVisible.value = true
}

function cancel() {
  drawerVisible.value = false
}

async function confirm() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  emit('confirm', { ...formData }, editIndex.value)
  drawerVisible.value = false
}

defineExpose({ open })
</script>
