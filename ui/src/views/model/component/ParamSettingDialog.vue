<template>
  <el-dialog
    v-model="dialogVisible"
    width="560px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <template #header>
      <h4 class="m-0">模型参数设置 - {{ model?.name }}</h4>
    </template>

    <el-form ref="formRef" :model="formData" label-position="top">
      <el-empty v-if="!formFields.length" description="该模型暂无参数配置" />
      <template v-for="(field, index) in formFields" :key="index">
        <el-form-item
          :label="getLabel(field)"
          :prop="field.field"
          :required="field.required"
          v-if="shouldShow(field)"
        >
          <el-input
            v-if="field.input_type === 'TextInput' || field.input_type === 'TextInputField'"
            v-model="formData[field.field]"
            v-bind="field.attrs || {}"
          />
          <el-switch
            v-else-if="field.input_type === 'SwitchInput' || field.input_type === 'Switch'"
            v-model="formData[field.field]"
          />
          <el-select
            v-else-if="field.input_type === 'SingleSelect' || field.input_type === 'Select'"
            v-model="formData[field.field]"
            style="width: 100%"
            v-bind="field.attrs || {}"
          >
            <el-option
              v-for="opt in (field.option_list || [])"
              :key="opt[field.value_field || 'value']"
              :label="opt[field.text_field || 'label'] || opt.label || opt.name"
              :value="opt[field.value_field || 'value']"
            />
          </el-select>
          <el-slider
            v-else-if="field.input_type === 'Slider'"
            v-model="formData[field.field]"
            v-bind="field.attrs || {}"
            style="width: 100%"
          />
          <el-input
            v-else-if="field.input_type === 'PasswordInput'"
            v-model="formData[field.field]"
            type="password"
            show-password
            v-bind="field.attrs || {}"
          />
          <el-input-number
            v-else-if="field.input_type === 'NumberInput'"
            v-model="formData[field.field]"
            v-bind="field.attrs || {}"
            style="width: 100%"
          />
          <el-input
            v-else
            v-model="formData[field.field]"
            v-bind="field.attrs || {}"
          />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="save" :loading="saving">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Model } from '@/api/type/model'
import type { FormField } from '@/api/type/common'
import modelApi from '@/api/model/model'
import { ElMessage } from 'element-plus'

const dialogVisible = ref(false)
const saving = ref(false)
const model = ref<Model | null>(null)
const formFields = ref<FormField[]>([])
const formData = ref<Record<string, any>>({})
const formRef = ref()

function getLabel(field: FormField): string {
  if (!field.label) return ''
  if (typeof field.label === 'string') return field.label
  return field.label.label || field.label.text || ''
}

function shouldShow(field: FormField): boolean {
  if (!field.relation_show_field_dict) return true
  const dict = field.relation_show_field_dict
  for (const depField of Object.keys(dict)) {
    const allowed = dict[depField]
    const actual = String(formData.value[depField] ?? '')
    if (allowed && Array.isArray(allowed) && !allowed.includes(actual)) return false
  }
  return true
}

function open(m: Model) {
  model.value = m
  dialogVisible.value = true
  saving.value = false
  formData.value = {}
  formFields.value = []

  modelApi.getModelParamsForm(m.id).then((res) => {
    formFields.value = res.data || []

    const defaults: Record<string, any> = {}
    for (const f of formFields.value) {
      if (f.default_value !== undefined && f.default_value !== null) {
        defaults[f.field] = f.default_value
      }
    }

    if (m.model_params_form && m.model_params_form.length > 0) {
      for (const param of m.model_params_form) {
        if (param.default_value !== undefined) {
          defaults[param.field || param.field] = param.default_value
        }
      }
    }

    formData.value = defaults
  })
}

function close() {
  dialogVisible.value = false
  model.value = null
  formFields.value = []
  formData.value = {}
}

async function save() {
  if (!model.value) return
  saving.value = true
  try {
    const params = formFields.value.map((f) => ({
      field: f.field,
      label: getLabel(f),
      input_type: f.input_type,
      required: f.required,
      default_value: formData.value[f.field] ?? f.default_value ?? '',
    }))

    await modelApi.updateModelParamsForm(model.value.id, params)
    ElMessage.success('保存成功')
    dialogVisible.value = false
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

defineExpose({ open, close })
</script>
