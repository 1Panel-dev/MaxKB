<template>
  <el-dialog
    :title="$t('common.setting')"
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
      @submit.prevent
    >
      <el-form-item :label="$t('chat.userInputSetting')">
        <el-select v-model="form.exposed_fields" multiple style="width: 100%">
          <el-option
            v-for="item in fieldOptions"
            :key="item.field"
            :label="getFieldLabel(item)"
            :value="item.field"
            :disabled="
              !allowedTypes.includes(item.input_type) ||
              (form.exposed_fields.length >= 3 && !form.exposed_fields.includes(item.field))
            "
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('common.title')" prop="menu_title">
        <el-input
          v-model="form.menu_title"
          maxlength="64"
          show-word-limit
          @blur="form.menu_title = form.menu_title.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const fieldOptions = ref<any[]>([])

const form = ref<any>({
  exposed_fields: [],
  menu_title: t('common.moreSettings'),
})

const rules = reactive({
  menu_title: [{ required: true, message: t('common.inputPlaceholder'), trigger: 'blur' }],
})

const allowedTypes = [
  'Model',
  'Knowledge',
  'SwitchInput',
  'DatePicker',
  'TreeSelect',
  'SingleSelect',
  'MultiSelect',
  'RadioCard',
  'RadioRow',
]
const dialogVisible = ref<boolean>(false)

const getFieldLabel = (item: any) => {
  if (typeof item.label === 'string') return item.label
  if (item.label?.label) return item.label.label
  return item.field
}

const open = (row: any, fields?: any[], setting?: any, legacyTitle?: string) => {
  form.value = {
    exposed_fields: setting?.exposed_fields || [],
    menu_title: setting?.menu_title || legacyTitle || t('common.moreSettings'),
  }
  fieldOptions.value = fields || []
  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', {
        exposed_fields: form.value.exposed_fields,
        menu_title: form.value.menu_title,
      })
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
