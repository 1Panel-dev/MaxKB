<template>
  <el-dialog
    :title="isEdit ? $t('common.param.editParam') : $t('common.param.addParam')"
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
      <el-form-item :label="$t('views.tool.form.paramName.label')" prop="field">
        <el-input
          v-model="form.field"
          :placeholder="$t('views.tool.form.paramName.placeholder')"
          maxlength="64"
          show-word-limit
          @blur="form.field = form.field.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('dynamicsForm.paramForm.name.label')" prop="label">
        <el-input
          v-model="form.label"
          :placeholder="$t('dynamicsForm.paramForm.name.placeholder')"
          :maxlength="128"
          show-word-limit
          @blur="form.label = form.label?.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('dynamicsForm.paramForm.desc.label')">
        <el-input
          v-model="form.desc"
          :placeholder="$t('dynamicsForm.paramForm.desc.placeholder')"
          :maxlength="128"
          show-word-limit
          @blur="form.desc = form.desc?.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('views.tool.form.dataType.label')">
        <el-select v-model="form.type">
          <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>

      <el-form-item :label="$t('dynamicsForm.paramForm.required.label')" @click.prevent>
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
const typeOptions = ['string', 'int', 'dict', 'array', 'float', 'boolean']
const emit = defineEmits(['refresh'])
const fieldFormRef = ref()
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
      message: t('views.tool.form.paramName.placeholder'),
      trigger: 'blur',
    },
  ],
  label: [
    {
      required: true,
      message: t('dynamicsForm.paramForm.name.placeholder'),
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
<style lang="scss" scoped></style>
