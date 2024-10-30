<template>
  <el-dialog
    :title="isEdit ? '编辑参数' : '添加参数'"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="参数" prop="variable">
        <el-input
          v-model="form.variable"
          placeholder="请输入参数"
          maxlength="64"
          show-word-limit
          @blur="form.variable = form.variable.trim()"
        />
      </el-form-item>

      <el-form-item label="是否必填" @click.prevent>
        <el-switch size="small" v-model="form.is_required"></el-switch>
      </el-form-item>
      <el-form-item
        label="默认值"
        prop="default_value"
        :rules="{
          required: form.is_required,
          message: '请输入默认值',
          trigger: 'blur'
        }"
      >
        <el-input
          v-model="form.default_value"
          placeholder="请输入默认值"
          @blur="form.name = form.name.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'

const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)

const form = ref<any>({
  name: '',
  variable: '',
  type: 'input',
  is_required: true,
  assignment_method: 'api_input',
  optionList: [''],
  default_value: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  variable: [
    { required: true, message: '请输入参数', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能输入字母数字和下划线', trigger: 'blur' }
  ]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      name: '',
      variable: '',
      type: 'input',
      is_required: true,
      assignment_method: 'api_input',
      optionList: [''],
      default_value: ''
    }
    isEdit.value = false
  }
})

const open = (row: any) => {
  if (row) {
    form.value = cloneDeep(row)
    isEdit.value = true
  }

  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
  isEdit.value = false
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value)
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
