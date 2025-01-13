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
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.functionLib.functionForm.form.paramName.label')" prop="name">
        <el-input
          v-model="form.name"
          :placeholder="$t('views.functionLib.functionForm.form.paramName.placeholder')"
          maxlength="64"
          show-word-limit
          @blur="form.name = form.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('views.functionLib.functionForm.form.dataType.label')">
        <el-select v-model="form.type">
          <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('views.functionLib.functionForm.form.source.label')">
        <el-select v-model="form.source">
          <el-option
            :label="$t('views.functionLib.functionForm.form.source.reference')"
            value="reference"
          />
          <el-option
            :label="$t('views.functionLib.functionForm.form.source.custom')"
            value="custom"
          />
        </el-select>
      </el-form-item>
      <el-form-item
        :label="$t('views.functionLib.functionForm.form.required.label')"
        @click.prevent
      >
        <el-switch size="small" v-model="form.is_required"></el-switch>
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
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
const typeOptions = ['string', 'int', 'dict', 'array', 'float']

const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)

const form = ref<any>({
  name: '',
  type: typeOptions[0],
  source: 'reference',
  is_required: true
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.functionLib.functionForm.form.paramName.placeholder'),
      trigger: 'blur'
    }
  ]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      name: '',
      type: typeOptions[0],
      source: 'reference',
      is_required: true
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
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
