<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'

const typeOptions = ['string', 'int', 'dict', 'array', 'float', 'boolean']
const emit = defineEmits(['refresh'])
const fieldFormRef = ref<FormInstance>()
const loading = ref<boolean>(false)
const isEdit = ref(false)
const form = ref<any>({
  field: '',
  type: typeOptions[0],
  label: '',
  desc: '',
  is_required: true,
})

const rules = reactive({
  field: [
    {
      required: true,
      message: '请输入参数名',
      trigger: 'blur',
    },
  ],
  label: [
    {
      required: true,
      message: '请输入显示名',
      trigger: 'blur',
    },
  ],
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      field: '',
      type: typeOptions[0],
      label: '',
      desc: '',
      is_required: true,
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

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value)
    }
  })
}

const close = () => {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <el-dialog
    :title="isEdit ? '编辑参数' : '添加参数'"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="参数名" prop="field">
        <el-input
          v-model="form.field"
          placeholder="请输入参数名"
          maxlength="64"
          show-word-limit
          @blur="form.field = form.field.trim()"
        />
      </el-form-item>
      <el-form-item label="显示名" prop="label">
        <el-input
          v-model="form.label"
          placeholder="请输入显示名"
          :maxlength="128"
          show-word-limit
          @blur="form.label = form.label?.trim()"
        />
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="form.desc"
          placeholder="请输入描述"
          :maxlength="128"
          show-word-limit
          @blur="form.desc = form.desc?.trim()"
        />
      </el-form-item>
      <el-form-item label="数据类型">
        <el-select v-model="form.type">
          <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>

      <el-form-item label="必填" @click.prevent>
        <el-switch size="small" v-model="form.is_required" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>