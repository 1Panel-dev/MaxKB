<template>
  <el-dialog
    :title="
      isEdit
        ? $t('views.template.templateForm.title.editParam')
        : $t('views.template.templateForm.title.addParam')
    "
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
      <el-form-item :label="$t('dynamicsForm.paramForm.field.label')" prop="variable">
        <el-input
          v-model="form.variable"
          :placeholder="$t('dynamicsForm.paramForm.field.placeholder')"
          maxlength="64"
          show-word-limit
          @blur="form.variable = form.variable.trim()"
        />
      </el-form-item>

      <el-form-item :label="$t('dynamicsForm.paramForm.required.label')" @click.prevent>
        <el-switch size="small" v-model="form.is_required"></el-switch>
      </el-form-item>
      <el-form-item
        :label="$t('dynamicsForm.default.label')"
        prop="default_value"
        :rules="{
          required: form.is_required,
          message: $t('dynamicsForm.default.placeholder'),
          trigger: 'blur'
        }"
      >
        <el-input
          v-model="form.default_value"
          :placeholder="$t('dynamicsForm.default.placeholder')"
          @blur="form.name = form.name.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? $t('common.save') : $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
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
  name: [{ required: true, message: t('dynamicsForm.paramForm.name.requiredMessage'), trigger: 'blur' }],
  variable: [
    { required: true, message:  t('dynamicsForm.paramForm.field.requiredMessage'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('dynamicsForm.paramForm.field.requiredMessage2'), trigger: 'blur' }
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
